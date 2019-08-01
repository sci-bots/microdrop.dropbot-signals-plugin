import logging

from debounce.async import Debounce
from logging_helpers import _L
from microdrop.app_context import get_app
from microdrop.plugin_manager import (PluginGlobals, Plugin, IPlugin,
                                      implements)
import microdrop as md
import numpy as np
import si_prefix as si
import trollius as asyncio

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

PluginGlobals.push_env('microdrop.managed')


class DropBotSignalsPlugin(Plugin):
    implements(IPlugin)

    plugin_name = 'dropbot_signals_plugin'
    version = __version__

    @property
    def name(self):
        return self.plugin_name

    @name.setter
    def name(self, value):
        pass

    @asyncio.coroutine
    def on_step_run(self, plugin_kwargs, signals):
        '''
        If DropBot plugin is found, log each DropBot signal during step.

        Notes
        -----
        DropBot signal callbacks are automatically disconnected when this
        coroutine exits.

        The following signals are logged::

         - 'capacitance-updated'
         - 'channels-updated'
         - 'chip-inserted'
         - 'chip-removed'
         - 'connected'
         - 'disconnected'

        The following signals are **NOT** logged::

         - 'flash-firmware'
         - 'halted'
         - 'no-power'
         - 'reboot'
         - 'reconnect'
         - 'shorts-detected'
         - 'version-mismatch'
        '''
        try:
            plugin = md.plugin_helpers.get_service_instance_by_name('dropbot_plugin')
            dropbot_signals = plugin.dropbot_signals
        except KeyError:
            _L().debug('DropBot plugin not found.')
            raise asyncio.Return()

        def _on_capacitance_updated(sender, **message):
            # New capacitance reading was received from the DropBot via a
            # `'capacitance-updated'` signal is emitted from the DropBot.
            _L().debug('DropBot capacitance reading received: %sF @ %sV',
                       si.si_format(message['new_value']),
                       si.si_format(message['V_a']))

        @asyncio.coroutine
        def _on_channels_updated(sender, **message):
            '''
            Message keys:
             - ``"n"``: number of actuated channels
             - ``"actuated"``: list of actuated channel identifiers.
             - ``"start"``: ms counter before setting shift registers
             - ``"end"``: ms counter after setting shift registers
            '''
            actuated_channels = message['actuated']
            if actuated_channels:
                app = get_app()
                actuated_electrodes = \
                    (app.dmf_device.actuated_electrodes(actuated_channels)
                     .dropna())
                actuated_areas = (app.dmf_device
                                  .electrode_areas.ix[actuated_electrodes
                                                      .values])
                self.actuated_area = actuated_areas.sum()
            else:
                self.actuated_area = 0
            # m^2 area
            area = self.actuated_area * (1e-3 ** 2)
            # Approximate area in SI units.
            value, pow10 = si.split(np.sqrt(area))
            si_unit = si.SI_PREFIX_UNITS[len(si.SI_PREFIX_UNITS) // 2 +
                                         pow10 // 3]
            status = ('actuated electrodes: %s (%.1f %sm^2)' %
                      (actuated_channels, value ** 2, si_unit))
            _L().debug(status)

        @asyncio.coroutine
        def on_inserted(sender, **message):
            _L().debug('DropBot reported chip was inserted.')

        @asyncio.coroutine
        def on_removed(sender, **message):
            _L().debug('DropBot reported chip was removed.')

        @asyncio.coroutine
        def _on_dropbot_connected(sender, **message):
            dropbot = message['dropbot']
            map(_L().debug, str(dropbot.properties).splitlines())

        @asyncio.coroutine
        def _on_dropbot_disconnected(sender, **message):
            _L().debug('DropBot connection lost.')

        # Call capacitance update callback _at most_ every 2 seconds.
        debounced_capacitance_update = \
            asyncio.coroutine(Debounce(_on_capacitance_updated, 1000,
                                       max_wait=2000, leading=True))

        signal_callbacks = {'capacitance-updated':
                            debounced_capacitance_update,
                            'channels-updated': _on_channels_updated,
                            'chip-inserted': on_inserted,
                            'chip-removed': on_removed,
                            'connected': _on_dropbot_connected,
                            'disconnected': _on_dropbot_disconnected}

        for name, callback in signal_callbacks.items():
            dropbot_signals.signal(name).connect(callback)

        # Do some work, e.g., wait for electrode actuation duration to pass.
        duration = (plugin_kwargs['microdrop.electrode_controller_plugin']
                    ['Duration (s)'])
        yield asyncio.From(asyncio.sleep(duration))


PluginGlobals.pop_env()
