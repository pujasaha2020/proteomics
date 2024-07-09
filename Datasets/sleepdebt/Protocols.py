# CR: Subject 3667A, ...., 3783A


def protocol1():
    N_recov = 1
    N_restr = 12
    Sleep = 8
    #Sleep_recover = 8

    t_awake_l = N_restr * [(24 - Sleep) * 60] + N_recov * [ 36 * 60]  # + [53] # N_recov*[24-Sleep_recover]
    t_sleep_l = N_restr * [Sleep * 60] + N_recov * [Sleep * 60]  # +N_recov*[Sleep_recover]

    return t_awake_l, t_sleep_l


# CR: Subject 41A9A, 41D3A, 4128A2T2, ...., 4276A
def protocol2():
    N_recov = 1
    N_rest = 11
    Sleep = 9
    Sleep_recover = 12

    t_awake_l = N_rest * [16 * 60] + 2 * [(24 - Sleep) * 60] + [39 * 60] + [16 * 60]
    t_sleep_l = N_rest * [8 * 60] + 2 * [Sleep * 60] + [Sleep_recover * 60] + [8 * 60]

    print(len(t_awake_l))
    print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol3():  # MPPG 8H TIB

    N_recov = 16
    # N_restr=
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_recov * [16 * 60]
    t_sleep_l = N_recov * [8 * 60]  # +N_recov*[Sleep_recover]

    # t_awake_l = [50]+N_recov*[24-Sleep_recover]
    # t_sleep_l = [12]+N_recov*[Sleep_recover]

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol4():  # MPPG 10H TIB

    N_recov = 5
    N_rest = 11
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [16 * 60] + N_recov * [14 * 60]
    t_sleep_l = N_rest * [8 * 60] + N_recov * [10 * 60]  # +N_recov*[Sleep_recover]

    # t_awake_l = [50]+N_recov*[24-Sleep_recover]
    # t_sleep_l = [12]+N_recov*[Sleep_recover]

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


def protocol5():  # 5H TIB for 21 days
    N_rest = 13
    N_recov = 9

    N_restr = 21
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [16 * 60] + N_restr * [19 * 60] + N_recov * [16 * 60]
    t_sleep_l = N_rest * [8 * 60] + N_restr * [5 * 60] + N_recov * [8 * 60]

    return t_awake_l, t_sleep_l


def protocol6():  # 5.6 H TIB for 21 days
    N_rest = 11
    N_recov = 9

    N_restr = 21

    t_awake_l = (
        N_rest * [16 * 60]
        + 2 * [14 * 60]
        + 1 * [972]
        + (N_restr - 1) * [1104]
        + [972]
        + (N_recov - 1) * [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60] + 2 * [10 * 60] + N_restr * [336] + N_recov * [10 * 60]
    )

    return t_awake_l, t_sleep_l


# dinges sample:
# 8 day protocol, 10 h of sleep on the first two baseline nights,
# followed by five nights of 4 hr sleep, followed by one recovery night.


def protocol7():
    N_rest = 13
    N_recov = 1

    N_restr = 5
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [14 * 60] + N_restr * [19 * 60] + N_recov * [16 * 60]
    t_sleep_l = N_rest * [10 * 60] + N_restr * [4 * 60] + N_recov * [8 * 60]

    return t_awake_l, t_sleep_l


# Force desynchrony study : 3453HY73
# 2 normal cycle of  (wake-sleep) 16hr - 8hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycle 27hr 23mins- 8 hr,
# ,8 cycles of 16hr- 8 hrs.


def protocol8_1():
    N_rest = 13
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [16 * 60] + N_restr * [980] + [1643] + N_recov * [16 * 60]
    t_sleep_l = N_rest * [8 * 60] + N_restr * [700] + [8 * 60] + N_recov * [8 * 60]

    return t_awake_l, t_sleep_l


# Force desynchrony study, 3557HY61
# 2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 32hr 5mins- 10 hrs, 8 cycles 14 hr-10 hr.


def protocol8_2():
    N_rest = 11
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + 2 * [14 * 60]
        + N_restr * [980]
        + [1925]
        + N_recov * [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + 2 * [10 * 60]
        + N_restr * [700]
        + [10 * 60]
        + N_recov * [10 * 60]
    )

    return t_awake_l, t_sleep_l


# Force desynchrony study, 2056HY75
# 2 normal cycle of  (wake-sleep) 16hr - 8hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 12hr - 4 hrs 53 mins,
# 1 ycle 10hr-8hr, 8 cycles 16 hr-8 hr.


def protocol8_3():
    N_rest = 13
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + N_restr * [980]
        + [12 * 60]
        + [10 * 60]
        + N_recov * [16 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60] + N_restr * [700] + [293] + [8 * 60] + N_recov * [8 * 60]
    )

    return t_awake_l, t_sleep_l


# Force desynchrony study, 3552HY62
# 2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 15hr 32mins- 10 hrs, 8 cycles 14 hr-10 hr.


def protocol8_4():
    N_rest = 11
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + 2 * [14 * 60]
        + N_restr * [980]
        + [932]
        + N_recov * [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + 2 * [10 * 60]
        + N_restr * [700]
        + [10 * 60]
        + N_recov * [10 * 60]
    )

    return t_awake_l, t_sleep_l


# Force desynchrony study, 26P2HY83
# 2 normal cycle of  (wake-sleep) 16hr - 8hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 12hr - 6hr,
# 1 ycle 10hr 2 min-8hr, 8 cycles 16 hr-8 hr.


def protocol8_5():
    N_rest = 13
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60] + N_restr * [980] + [12 * 60] + [602] + N_recov * [16 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60] + N_restr * [700] + [6 * 60] + [8 * 60] + N_recov * [8 * 60]
    )

    return t_awake_l, t_sleep_l


# Force desynchrony study, 3453HY52
# 2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 20hr 33mins- 10 hrs, 8 cycles 14 hr-10 hr.


def protocol8_6():
    N_rest = 11
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + 2 * [14 * 60]
        + N_restr * [980]
        + [1233]
        + N_recov * [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + 2 * [10 * 60]
        + N_restr * [700]
        + [10 * 60]
        + N_recov * [10 * 60]
    )

    return t_awake_l, t_sleep_l


# Force desynchrony study, 3536HY83
# 2 normal cycle of  (wake-sleep) 16hr - 8hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 19hr 47mins- 8 hrs, 8 cycles 16 hr-8 hr.


def protocol8_7():
    N_rest = 13
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [16 * 60] + N_restr * [980] + [1187] + N_recov * [16 * 60]
    t_sleep_l = N_rest * [8 * 60] + N_restr * [700] + [8 * 60] + N_recov * [8 * 60]

    return t_awake_l, t_sleep_l


# Force desynchrony study, 3536HY52
# 2 normal cycle of  (wake-sleep) 14hr - 10hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 18hr 44mins- 10 hrs, 8 cycles 14 hr-10 hr.


def protocol8_8():
    N_rest = 11
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + 2 * [14 * 60]
        + N_restr * [980]
        + [1124]
        + N_recov * [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + 2 * [10 * 60]
        + N_restr * [700]
        + [10 * 60]
        + N_recov * [10 * 60]
    )

    return t_awake_l, t_sleep_l


# Force desynchrony study, 3552HY73
# 2 normal cycle of  (wake-sleep) 16hr - 8hr , 18 cycle of 16hr 20m- 11hr 40m, 1 cycles of 19hr 9mins- 8 hrs, 8 cycles 16 hr-8 hr.


def protocol8_9():
    N_rest = 13
    N_recov = 8

    N_restr = 18
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [16 * 60] + N_restr * [980] + [1149] + N_recov * [16 * 60]
    t_sleep_l = N_rest * [8 * 60] + N_restr * [700] + [8 * 60] + N_recov * [8 * 60]

    return t_awake_l, t_sleep_l


# FAA Control sample :


def protocol9():
    N_rest = 11
    N_recov = 1

    N_restr = 8
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = N_rest * [16 * 60] + [13 * 60] + [13 * 60] + N_restr * [16 * 60]
    t_sleep_l = N_rest * [8 * 60] + [12 * 60] + [10 * 60] + N_restr * [8 * 60]

    # print(t_awake_l)
    # print(t_sleep_l)

    return t_awake_l, t_sleep_l


# FAA TSD sample :


def protocol10():
    N_rest = 11  # 11
    N_recov = 3

    N_restr = 1
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + [13 * 60]
        + [13 * 60]
        + N_restr * [62 * 60]
        + [14 * 60]
        + N_recov * [16 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + [12 * 60]
        + [10 * 60]
        + N_restr * [10 * 60]
        + [10 * 60]
        + N_recov * [8 * 60]
    )

    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l


# FAA CSRN sample :


def protocol11():
    N_rest = 11
    # N_recov=2

    N_restr = 4
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + [13 * 60]
        + [13 * 60]
        + [15 * 60]
        + N_restr * [19 * 60]
        + [18 * 60]
        + [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + [12 * 60]
        + [10 * 60]
        + [5 * 60]
        + N_restr * [5 * 60]
        + [10 * 60]
        + [10 * 60]
    )

    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l


# FAA CSRD sample :


def protocol12():
    N_rest = 11  # 11
    N_recov = 2

    N_restr = 4
    # Sleep = 8
    # Sleep_recover = 8

    t_awake_l = (
        N_rest * [16 * 60]
        + [13 * 60]
        + [13 * 60]
        + [27 * 60]
        + N_restr * [19 * 60]
        + [6 * 60]
        + [14 * 60]
    )
    t_sleep_l = (
        N_rest * [8 * 60]
        + [12 * 60]
        + [10 * 60]
        + [5 * 60]
        + N_restr * [5 * 60]
        + [10 * 60]
        + [10 * 60]
    )

    # t_awake_l =   N_rest*[16*60]+  [27*60] + N_restr*[19*60] +  [6*60]+ [14*60]
    # t_sleep_l =   N_rest*[8*60] + [5*60] +  N_restr*[5*60] +  [10*60] + [10*60]
    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l


# Zeitzer sample
# "990023" "990002" "990004" "990012" "990022" "990039" "990043" "990044" "990067" "990095" "990100" "990104" "990110" "990112" "990115" "990119" "990120" "990130" "990134"
# "990136" "990141" "990143" "990150" "990003" "990055" "990132" "990051" "990052" "990068" "990085" "990088" "990116" "990131" "990032" "990037" "990047" "990049" "990050"
# "990128"


def protocol13():

    N_rest = 11  # 11

    t_awake_l = N_rest * [16 * 60] + [966] + [540]
    t_sleep_l = N_rest * [8 * 60] + [480] + [480]

    # t_awake_l =   N_rest*[16*60]+  [27*60] + N_restr*[19*60] +  [6*60]+ [14*60]
    # t_sleep_l =   N_rest*[8*60] + [5*60] +  N_restr*[5*60] +  [10*60] + [10*60]
    print(t_awake_l)
    print(t_sleep_l)

    return t_awake_l, t_sleep_l
