# Interpolation formula:
# r(T) = r_1 + (T - T_1)/(T_2 - T_1) * (r_2 - r_1)
# with T_2 > T_1
# For T > 1M assume r_T = r(T_1M)

def interpolate_rate(df):
    
    yte = df["yte"]

    r1M = df["US1M"]
    r3M = df["US3M"]
    r6M = df["US6M"]
    r1Y = df["US1Y"]

    if yte <= 1/12:
        r = r1M
    elif 1/12 < yte <= 0.25:
        r = r1M + (yte - 1/12) / (0.25 - 1/12) * (r3M - r1M)
    elif 0.25 < yte <= 0.5:
        r = r3M + (yte - 0.25) / (0.5 - 0.25) * (r6M - r3M)
    else:
        r = r6M + (yte - 0.5) / (1 - 0.5) * (r1Y - r6M)

    return r