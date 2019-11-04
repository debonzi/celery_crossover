def test_worker_1(worker_1):
    from examples.project_1.project import simple
    assert simple.delay().get(timeout=10) == 'HELLO 1'


def test_worker_2(worker_2):
    from examples.project_2.project import simple
    assert simple.delay().get(timeout=10) == 'HELLO 2'


def test_auto_callback(worker_1, worker_2, p1_client, redis):
    """
    P2 call P1 `plus` task with P2 `plus_callback` as P1 `plus` callback.
    p1 `plus` has @crossover.callback(auto_callback=True) decorator.

    P2 p1_client.plus   ->    P1
    P2 plus_callback    <-    P1

    P2 stores the value received by plus_callback into redis
    so we can check its value
    """
    from examples.project_2.project import plus_callback

    p1_client.plus(x=340, y=210, callback=plus_callback)
    assert redis.get('plus_callback') == b'550'

    dispatch_queue_time = redis.get('dispatch_queue_time')
    assert dispatch_queue_time is not None
    assert isinstance(float(dispatch_queue_time), float)


def test_callback_meta(worker_1, worker_2, p1_client, redis):
    """
    P2 call P1 `times` task with P2 `times_callback` as P1 `times` callback.
    P1 `times` has @crossover.callback(bind_callback_meta=True) decorator and
    will get `callback_meta` as first argument.
    P1 `times` will call P1 `calculate_times` task passing `callback_meta`.
    P1 `calculate_times` will instantiate a crossover.CallBack object and
    send the result to P2 `times_callback`


    P2 p1_client.plus   ->    P1 (plus)  ->  P1 (calculate_times)
    P2 times_callback    <-----------------   P1

    P2 stores the value received by times_callback into redis
    so we can check its value
    """
    from examples.project_2.project import times_callback

    p1_client.times(x=340, y=210, callback=times_callback)
    assert redis.get('times_callback') == b'71400'

    dispatch_queue_time = redis.get('dispatch_queue_time')
    assert dispatch_queue_time is not None
    assert isinstance(float(dispatch_queue_time), float)
