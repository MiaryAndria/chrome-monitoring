## lien pour trouver readmask nécessaires 
https://developers.google.com/chrome/management/reference/rest/v1/customers.telemetry.devices

# liste readmask telemetry device
{
  "name": string,
  "customer": string,
  "orgUnitId": string,
  "deviceId": string,
  "serialNumber": string,
  "cpuInfo": [
    {
      object (CpuInfo)
    }
  ],
  "cpuStatusReport": [
    {
      object (CpuStatusReport)
    }
  ],
  "memoryInfo": {
    object (MemoryInfo)
  },
  "memoryStatusReport": [
    {
      object (MemoryStatusReport)
    }
  ],
  "networkInfo": {
    object (NetworkInfo)
  },
  "networkStatusReport": [
    {
      object (NetworkStatusReport)
    }
  ],
  "networkDiagnosticsReport": [
    {
      object (NetworkDiagnosticsReport)
    }
  ],
  "osUpdateStatus": [
    {
      object (OsUpdateStatus)
    }
  ],
  "graphicsInfo": {
    object (GraphicsInfo)
  },
  "graphicsStatusReport": [
    {
      object (GraphicsStatusReport)
    }
  ],
  "batteryInfo": [
    {
      object (BatteryInfo)
    }
  ],
  "batteryStatusReport": [
    {
      object (BatteryStatusReport)
    }
  ],
  "storageInfo": {
    object (StorageInfo)
  },
  "storageStatusReport": [
    {
      object (StorageStatusReport)
    }
  ],
  "thunderboltInfo": [
    {
      object (ThunderboltInfo)
    }
  ],
  "audioStatusReport": [
    {
      object (AudioStatusReport)
    }
  ],
  "bootPerformanceReport": [
    {
      object (BootPerformanceReport)
    }
  ],
  "heartbeatStatusReport": [
    {
      object (HeartbeatStatusReport)
    }
  ],
  "kioskAppStatusReport": [
    {
      object (KioskAppStatusReport)
    }
  ],
  "networkBandwidthReport": [
    {
      object (NetworkBandwidthReport)
    }
  ],
  "peripheralsReport": [
    {
      object (PeripheralsReport)
    }
  ],
  "appReport": [
    {
      object (AppReport)
    }
  ],
  "runtimeCountersReport": [
    {
      object (RuntimeCountersReport)
    }
  ]
}

# Pour les événements : 
https://developers.google.com/chrome/management/reference/rest/v1/customers.telemetry.events (ressource TelemetryEvent)

# liste readmask telemetry events 
{
  "name": string,
  "device": {
    object (TelemetryDeviceInfo)
  },
  "user": {
    object (TelemetryUserInfo)
  },
  "reportTime": string,
  "eventType": enum (EventType),
  "audioSevereUnderrunEvent": {
    object (TelemetryAudioSevereUnderrunEvent)
  },
  "usbPeripheralsEvent": {
    object (TelemetryUsbPeripheralsEvent)
  },
  "networkStateChangeEvent": {
    object (TelemetryNetworkConnectionStateChangeEvent)
  },
  "httpsLatencyChangeEvent": {
    object (TelemetryHttpsLatencyChangeEvent)
  },
  "wifiSignalStrengthEvent": {
    object (TelemetryNetworkSignalStrengthEvent)
  },
  "vpnConnectionStateChangeEvent": {
    object (TelemetryNetworkConnectionStateChangeEvent)
  },
  "appInstallEvent": {
    object (TelemetryAppInstallEvent)
  },
  "appUninstallEvent": {
    object (TelemetryAppUninstallEvent)
  },
  "appLaunchEvent": {
    object (TelemetryAppLaunchEvent)
  },
  "osCrashEvent": {
    object (TelemetryOsCrashEvent)
  },
  "externalDisplaysEvent": {
    object (TelemetryExternalDisplayEvent)
  }
}

# Pour les utilisateurs : 
https://developers.google.com/chrome/management/reference/rest/v1/customers.telemetry.users (ressource TelemetryUser)

# Guide avec exemples de requêtes déjà testées (celui qui nous a donné le readMask qui fonctionne) : 
https://developers.google.com/chrome/management/guides/samples_telemetryapi