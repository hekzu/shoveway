# ShoveWay

Shove it in my gateway.

Tired of trying to use Pushgateway to push metrics to Prometheus? No more!

Now Prometheus, a product created in the last 5 years, has a way to push metrics which DOESN'T use a protocol that looks like it was designed before C was mainstream!

Existing features:
1) POST metrics in JSON format
2) Expose metrics in Prometheus OpenMetrics format
3) Persistent storage

Coming soon:
1) Clustering
2) Redis storage
3) More supported formats (other than JSON)
