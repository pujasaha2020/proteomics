"""Module providing a function  for each protocol."""

# CR: Subject 3667A, ...., 3783A


def protocol1():
    """Function defining protocol "mri", one night of 8 hour sleep,
    36 hours awake, 8 hours recovery night ."""
    n_recovery = 1
    n_rest = 12
    sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [(24 - sleep) * 60] + n_recovery * [36 * 60]
    # + [53] # n_recovery*[24-sleep_recover]
    t_sleep_l = n_rest * [sleep * 60] + n_recovery * [sleep * 60]
    # +n_recovery*[sleep_recover]

    return t_awake_l, t_sleep_l


def protocol2():
    """
    # CR: Subject 41A9A, 41D3A, 4128A2T2, ...., 4276A
    Function defining protocol "5day", two night of 9 hour sleep,
    39 hours awake, 12 hours recovery night, 16-8 hours normal schedule ."""
    n_rest = 11
    sleep = 9

    t_awake_l = n_rest * [16 * 60] + 2 * [(24 - sleep) * 60] + [39 * 60] + [16 * 60]
    t_sleep_l = n_rest * [8 * 60] + 2 * [sleep * 60] + [12 * 60] + [8 * 60]

    # print(len(t_awake_l))
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol3():
    """MPPG 8H Time in bed"""

    n_recovery = 16
    # n_rest=
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_recovery * [16 * 60]
    t_sleep_l = n_recovery * [8 * 60]  # +n_recovery*[sleep_recover]

    # t_awake_l = [50]+n_recovery*[24-sleep_recover]
    # t_sleep_l = [12]+n_recovery*[sleep_recover]

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol4():
    """MPPG 10H Time in bed"""

    n_recovery = 5
    n_rest = 11
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [16 * 60] + n_recovery * [14 * 60]
    t_sleep_l = n_rest * [8 * 60] + n_recovery * [10 * 60]
    # +n_recovery*[sleep_recover]

    # t_awake_l = [50]+n_recovery*[24-sleep_recover]
    # t_sleep_l = [12]+n_recovery*[sleep_recover]

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol5():
    """5H TIB for 21 days"""
    n_rest = 13
    n_recovery = 9

    n_exp = 21
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [16 * 60] + n_exp * [19 * 60] + n_recovery * [16 * 60]
    t_sleep_l = n_rest * [8 * 60] + n_exp * [5 * 60] + n_recovery * [8 * 60]

    return t_awake_l, t_sleep_l


def protocol6():
    """5.6 H TIB for 21 days"""
    n_rest = 11
    n_recovery = 9

    n_exp = 21

    t_awake_l = (
        n_rest * [16 * 60]
        + 2 * [14 * 60]
        + 1 * [972]
        + (n_exp - 1) * [1104]
        + [972]
        + (n_recovery - 1) * [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60] + 2 * [10 * 60] + n_exp * [336] + n_recovery * [10 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol7():
    """dinges sample:
    8 day protocol, 10 h of sleep on the first two baseline nights,
    followed by five nights of 4 hr sleep, followed by one recovery night.
    """
    n_rest = 13
    n_recovery = 1

    n_exp = 5
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [14 * 60] + n_exp * [19 * 60] + n_recovery * [16 * 60]
    t_sleep_l = n_rest * [10 * 60] + n_exp * [4 * 60] + n_recovery * [8 * 60]

    return t_awake_l, t_sleep_l


def protocol8_1():
    """Force desynchrony study : 3453HY73 , 2 normal cycle of  (wake-sleep) 16hr - 8hr ,
    18 cycle of 16hr 20m- 11hr 40m, 1 cycle 27hr 23mins- 8 hr,
    8 cycles of 16hr- 8 hrs."""
    n_rest = 13
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [16 * 60] + n_exp * [980] + [1643] + n_recovery * [16 * 60]
    t_sleep_l = n_rest * [8 * 60] + n_exp * [700] + [8 * 60] + n_recovery * [8 * 60]

    return t_awake_l, t_sleep_l


def protocol8_2():
    """Force desynchrony study, 3557HY61
    2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m,
    1 cycles of 32hr 5mins- 10 hrs, 8 cycles 14 hr-10 hr.
    """
    n_rest = 11
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + 2 * [14 * 60]
        + n_exp * [980]
        + [1925]
        + n_recovery * [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + 2 * [10 * 60]
        + n_exp * [700]
        + [10 * 60]
        + n_recovery * [10 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol8_3():
    """
    Force desynchrony study, 2056HY75
    2 normal cycle of  (wake-sleep) 16hr - 8hr ,
    18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 12hr - 4 hrs 53 mins,
    1 cycle 10hr-8hr, 8 cycles 16 hr-8 hr.
    """
    n_rest = 13
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + n_exp * [980]
        + [12 * 60]
        + [10 * 60]
        + n_recovery * [16 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60] + n_exp * [700] + [293] + [8 * 60] + n_recovery * [8 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol8_4():
    """
    Force desynchrony study, 3552HY62
    2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m,
    1 cycles of 15hr 32mins- 10 hrs, 8 cycles 14 hr-10 hr.
    """
    n_rest = 11
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + 2 * [14 * 60]
        + n_exp * [980]
        + [932]
        + n_recovery * [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + 2 * [10 * 60]
        + n_exp * [700]
        + [10 * 60]
        + n_recovery * [10 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol8_5():
    """
    Force desynchrony study, 26P2HY83
    2 normal cycle of  (wake-sleep) 16hr - 8hr ,
    18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 12hr - 6hr,
    1 cycle 10hr 2 min-8hr, 8 cycles 16 hr-8 hr.
    """
    n_rest = 13
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60] + n_exp * [980] + [12 * 60] + [602] + n_recovery * [16 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60] + n_exp * [700] + [6 * 60] + [8 * 60] + n_recovery * [8 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol8_6():
    """
    Force desynchrony study, 3453HY52
    2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m,
    1 cycles of 20hr 33mins- 10 hrs, 8 cycles 14 hr-10 hr.
    """
    n_rest = 11
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + 2 * [14 * 60]
        + n_exp * [980]
        + [1233]
        + n_recovery * [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + 2 * [10 * 60]
        + n_exp * [700]
        + [10 * 60]
        + n_recovery * [10 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol8_7():
    """
    Force desynchrony study, 3536HY83
    2 normal cycle of  (wake-sleep) 16hr - 8hr ,
    18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 19hr 47mins- 8 hrs, 8 cycles 16 hr-8 hr.
    """
    n_rest = 13
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [16 * 60] + n_exp * [980] + [1187] + n_recovery * [16 * 60]
    t_sleep_l = n_rest * [8 * 60] + n_exp * [700] + [8 * 60] + n_recovery * [8 * 60]

    return t_awake_l, t_sleep_l


def protocol8_8():
    """
    Force desynchrony study, 3536HY52
    2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m,
    1 cycles of 18hr 44mins- 10 hrs, 8 cycles 14 hr-10 hr.
    """
    n_rest = 11
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + 2 * [14 * 60]
        + n_exp * [980]
        + [1124]
        + n_recovery * [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + 2 * [10 * 60]
        + n_exp * [700]
        + [10 * 60]
        + n_recovery * [10 * 60]
    )

    return t_awake_l, t_sleep_l


def protocol8_9():
    """
    Force desynchrony study, 3552HY73
    2 normal cycle of  (wake-sleep) 16hr - 8hr ,
    18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 19hr 9mins- 8 hrs, 8 cycles 16 hr-8 hr.
    """
    n_rest = 13
    n_recovery = 8

    n_exp = 18
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [16 * 60] + n_exp * [980] + [1149] + n_recovery * [16 * 60]
    t_sleep_l = n_rest * [8 * 60] + n_exp * [700] + [8 * 60] + n_recovery * [8 * 60]

    return t_awake_l, t_sleep_l


def protocol9():
    """FAA Control sample"""
    n_rest = 11

    n_exp = 8
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = n_rest * [16 * 60] + [13 * 60] + [13 * 60] + n_exp * [16 * 60]
    t_sleep_l = n_rest * [8 * 60] + [12 * 60] + [10 * 60] + n_exp * [8 * 60]

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol10():
    """FAA TSD sample"""
    n_rest = 11  # 11
    n_recovery = 3

    n_exp = 1
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + [13 * 60]
        + [13 * 60]
        + n_exp * [62 * 60]
        + [14 * 60]
        + n_recovery * [16 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + [12 * 60]
        + [10 * 60]
        + n_exp * [10 * 60]
        + [10 * 60]
        + n_recovery * [8 * 60]
    )

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol11():
    """# FAA CSRN sample"""
    n_rest = 11
    # n_recovery=2

    n_exp = 4
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + [13 * 60]
        + [13 * 60]
        + [15 * 60]
        + n_exp * [19 * 60]
        + [18 * 60]
        + [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + [12 * 60]
        + [10 * 60]
        + [5 * 60]
        + n_exp * [5 * 60]
        + [10 * 60]
        + [10 * 60]
    )

    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol12():
    """FAA CSRD sample"""
    n_rest = 11  # 11
    n_exp = 4
    # sleep = 8
    # sleep_recover = 8

    t_awake_l = (
        n_rest * [16 * 60]
        + [13 * 60]
        + [13 * 60]
        + [27 * 60]
        + n_exp * [19 * 60]
        + [6 * 60]
        + [14 * 60]
    )
    t_sleep_l = (
        n_rest * [8 * 60]
        + [12 * 60]
        + [10 * 60]
        + [5 * 60]
        + n_exp * [5 * 60]
        + [10 * 60]
        + [10 * 60]
    )

    # t_awake_l =   n_rest*[16*60]+  [27*60] + n_rest*[19*60] +  [6*60]+ [14*60]
    # t_sleep_l =   n_rest*[8*60] + [5*60] +  n_rest*[5*60] +  [10*60] + [10*60]
    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol13():
    """
    Zeitzer sample
    "990023" "990002" "990004" "990012" "990022" "990039" "990043" "990044"
    "990067" "990095" "990100" "990104" "990110" "990112" "990115" "990119"
    "990120" "990130" "990134" "990136" "990141" "990143" "990150" "990003"
    "990055" "990132" "990051" "990052" "990068" "990085" "990088" "990116"
    "990131" "990032" "990037" "990047" "990049" "990050" "990128"
    """

    n_rest = 11  # 11

    t_awake_l = n_rest * [16 * 60] + [966] + [540]
    t_sleep_l = n_rest * [8 * 60] + [480] + [480]

    # t_awake_l =   n_rest*[16*60]+  [27*60] + n_rest*[19*60] +  [6*60]+ [14*60]
    # t_sleep_l =   n_rest*[8*60] + [5*60] +  n_rest*[5*60] +  [10*60] + [10*60]
    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l
