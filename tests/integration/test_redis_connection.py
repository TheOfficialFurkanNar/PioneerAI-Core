import redis

def test_redis_ping():
    """
    Redis sunucusunun ayağa kalktığını ve yanıt verdiğini doğrular.
    """
    r = redis.Redis(host="localhost", port=6379, db=0)
    # Sunucuya ping at ve True döndüğünü assert et
    assert r.ping() is True