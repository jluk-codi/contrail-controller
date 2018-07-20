import string

template = string.Template("""
[Unit]
Description="Tungsten Tor Agent service"
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/tungsten-tor-agent --config_file /etc/tungsten/$__tungsten_tor_agent_conf_file__
PIDFile=/var/run/tungsten/tungsten-tor-agent.pid
TimeoutStopSec=0
Restart=always
ExecStop=/bin/kill -s KILL $MAINPID
PrivateTmp=yes
ProtectHome=yes
ReadOnlyDirectories=/
ReadWriteDirectories=-/var/crashes
ReadWriteDirectories=-/var/log/tungsten
ReadWriteDirectories=-/var/lib/tungsten
ReadWriteDirectories=-/dev

[Install]
WantedBy=multi-user.target
""")
