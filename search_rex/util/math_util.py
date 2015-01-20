def exp_decay(value, time_t0, time_t, interval, half_life, max_age):
    if time_t > time_t0:
        return value
    age = (time_t0 - time_t).total_seconds() // interval.total_seconds()
    if age > max_age:
        return 0.0
    return value * 2**(-(age)/float(half_life))
