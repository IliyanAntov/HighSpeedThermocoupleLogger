record_folder_dir = "./logs/"
device_vid = 0x0483
device_pid = 0x5740
service_msg_size = 256

generator_log_interval_ms = 1
generator_log_start_time_ms = 50
therapy_parameters_first_line = "Therapy parameters:"
therapy_parameters_last_line = "-End-"
log_column_names = {
    "U": "U[10mV]",
    "I": "I[100uA]",
    "Z": "Z[Ohm]",
    "P": "P[uW]",
    "Phase": "F[Deg]"
}
excel_column_names = {
    "U": "U[V]",
    "I": "I[A]",
    "Z": "Z[Ω]",
    "P": "P[W]",
    "Phase": "φ[°]"
}
plot_label_names = {
    "U": "Voltage",
    "I": "Current",
    "Z": "Impedance",
    "P": "Power",
    "Phase": "Phase"
}
log_column_scales = {
    "U": 10 * 10**-3,
    "I": 100 * 10**-6,
    "Z": 1,
    "P": 10**-6,
    "Phase": 1
}
log_meaningful_float_characters = {
    "U": 2,
    "I": 4,
    "Z": 0,
    "P": 6,
    "Phase": 2
}

record_length_ms_min_max = {
    "min": 1,
    "max": 2000
}
record_interval_us_min_max = {
    "min": 10,
    "max": 1000
}

inamp_gain = ((9900 / 54.9) + 1)
voltage_to_temp = {
    "J": {
        # -210 to 0°C // -8 095 to 0 µV
        "-": [
            0,
            1.9528268 * 10**(-2),
            1.9528268 * 10**(-2),
            -1.0752178 * 10**(-9),
            -5.9086933 * 10**(-13),
            -1.7256713 * 10**(-16),
            -2.8131513 * 10**(-20),
            -2.3963370 * 10**(-24),
            -8.3823321 * 10**(-29)
        ],
        # 0 to 760°C // 0 to 42 919 µV
        "+": [
            0,
            1.978425 * 10**(-2),
            -2.001204 * 10**(-7),
            1.036969 * 10**(-11),
            -2.549687 * 10**(-16),
            3.585153 * 10**(-21),
            -5.344285 * 10**(-26),
            5.099890 * 10**(-31)
        ]
    },
    "K": {
        # -200 to 0°C // -5 891 to 0 µV
        "-": [
            0,
            2.5173462 * 10**(-2),
            -1.1662878 * 10**(-6),
            -1.0833638 * 10**(-9),
            -8.9773540 * 10**(-13),
            -3.7342377 * 10**(-16),
            -8.6632643 * 10**(-20),
            -1.0450598 * 10**(-23),
            -5.1920577 * 10**(-28)
        ],
        # 0 to 500°C // 0 to 20 644 µV
        "+": [
            0,
            2.508355 * 10**(-2),
            7.860106 * 10**(-8),
            -2.503131 * 10**(-10),
            8.315270 * 10**(-14),
            -1.228034 * 10**(-17),
            9.804036 * 10**(-22),
            -4.413030 * 10**(-26),
            1.057734 * 10**(-30),
            -1.052755 * 10**(-35)
        ],
    },
    "T": {
        # -200 to 0°C // -5 603 to 0 µV
        "-": [
            0,
            2.5929192 * 10**(-2),
            -2.1316967 * 10**(-7),
            7.9018692 * 10**(-10),
            4.2527777 * 10**(-13),
            1.3304473 * 10**(-16),
            2.0241446 * 10**(-20),
            1.2668171 * 10**(-24)
        ],
        # 0 to 400°C // 0 to 20 872 µV
        "+": [
            0,
            2.592800 * 10**(-2),
            -7.602961 * 10**(-7),
            4.637791 * 10**(-11),
            -2.165394 * 10**(-15),
            6.048144 * 10**(-20),
            -7.293422 * 10**(-25)
        ],
    },
    "E": {
        # -200 to 0°C // -8 825 to 0 µV
        "-": [
            0,
            1.6977288 * 10**(-2),
            -4.3514970 * 10**(-7),
            -1.5859697 * 10**(-10),
            -9.2502871 * 10**(-14),
            -2.6084314 * 10**(-17),
            -4.1360199 * 10**(-21),
            -3.4034030 * 10**(-25),
            -1.1564890 * 10**(-29)
        ],
        # 0 to 1000°C // 0 to 76 373 µV
        "+": [
            0,
            1.7057035 * 10**(-2),
            -2.3301759 * 10**(-7),
            6.5435585 * 10**(-12),
            -7.3562749 * 10**(-17),
            -1.7896001 * 10**(-21),
            8.4036165 * 10**(-26),
            -1.3735879 * 10**(-30),
            1.0629823 * 10**(-35),
            -3.2447087 * 10**(-41)
        ],
    }
}

temp_to_voltage = {
    "J": {
        # -210 to 760°C
        "-": [
            0,
            5.0381187815 * 10**(1),
            3.0475836930 * 10**(-2),
            -8.5681065720 * 10**(-5),
            1.3228195295 * 10**(-7),
            -1.7052958337 * 10**(-10),
            2.0948090697 * 10**(-13),
            -1.2538395336 * 10**(-16),
            1.5631725697 * 10**(-20)
        ],
        # -210 to 760°C
        "+": [
            0,
            5.0381187815 * 10 ** (1),
            3.0475836930 * 10 ** (-2),
            -8.5681065720 * 10 ** (-5),
            1.3228195295 * 10 ** (-7),
            -1.7052958337 * 10 ** (-10),
            2.0948090697 * 10 ** (-13),
            -1.2538395336 * 10 ** (-16),
            1.5631725697 * 10 ** (-20)
        ],
    },
    "K": {
        # -270 to 0°C
        "-": [
            0,
            3.9450128025 * 10**(1),
            2.3622373598 * 10**(-2),
            -3.2858906784 * 10**(-4),
            -4.9904828777 * 10**(-6),
            -6.7509059173 * 10**(-8),
            -5.7410327428 * 10**(-10),
            -3.1088872894 * 10**(-12),
            -1.0451609365 * 10**(-14),
            -1.9889266878 * 10**(-17),
            -1.6322697486 * 10**(-20)
        ],
        # 0 to 1372°C
        "+": [
            -1.7600413686 * 10 ** (1),
            3.8921204975 * 10 ** (1),
            1.8558770032 * 10 ** (-2),
            -9.9457592874 * 10 ** (-5),
            3.1840945719 * 10 ** (-7),
            -5.6072844889 * 10 ** (-10),
            5.6075059059 * 10 ** (-13),
            -3.2020720003 * 10 ** (-16),
            9.7151147152 * 10 ** (-20),
            -1.2104721275 * 10 ** (-23)
        ],
        "alpha": [
            1.185976 * 10**(2),
            -1.183432 * 10**(-4)
        ]
    },
    "T": {
        # -270 to 0°C
        "-": [
            0,
            3.8748106364 * 10**(1),
            4.4194434347 * 10**(-2),
            1.1844323105 * 10**(-4),
            2.0032973554 * 10**(-5),
            9.0138019559 * 10**(-7),
            2.2651156593 * 10**(-8),
            3.6071154205 * 10**(-10),
            3.8493939883 * 10**(-12),
            2.8213521925 * 10**(-14),
            1.4251594779 * 10**(-16),
            4.8768662286 * 10**(-19),
            1.0795539270 * 10**(-21),
            1.3945027062 * 10**(-24),
            7.9795153927 * 10**(-28)
        ],
        # 0 to 400°C
        "+": [
            0,
            3.8748106364 * 10**(1),
            3.3292227880 * 10**(-2),
            2.0618243404 * 10**(-4),
            -2.1882256846 * 10**(-6),
            1.0996880928 * 10**(-8),
            -3.0815758772 * 10**(-11),
            4.5479135290 * 10**(-14),
            2.7512901673 * 10**(-17)
        ],
    },
    "E": {
        # -270 to 0°C
        "-": [
            0,
            5.8665508708 * 10 ** (1),
            4.5410977124 * 10 ** (-2),
            -7.7998048686 * 10 ** (-4),
            -2.5800160843 * 10 ** (-5),
            -5.9452583057 * 10 ** (-7),
            -9.3214058667 * 10 ** (-9),
            -1.0287605534 * 10 ** (-10),
            -8.0370123621 * 10 ** (-13),
            -4.3979497391 * 10 ** (-15),
            -1.6414776355 * 10 ** (-17),
            -3.9673619516 * 10 ** (-20),
            -5.5827328721 * 10 ** (-23),
            -3.4657842013 * 10 ** (-26)
        ],
        # 0 to 400°C
        "+": [
            0,
            5.8665508710 * 10 ** (1),
            4.5032275582 * 10 ** (-2),
            2.8908407212 * 10 ** (-5),
            -3.3056896652 * 10 ** (-7),
            6.5024403270 * 10 ** (-10),
            -1.9197495504 * 10 ** (-1),
            -1.2536600497 * 10 ** (-15),
            2.1489217569 * 10 ** (-18),
            -1.4388041782 * 10 ** (-21),
            3.5960899481 * 10 ** (-25)
        ],
    },
}
