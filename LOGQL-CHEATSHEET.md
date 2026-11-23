# LogQL Cheatsheet — i-type nang live sa Grafana Explore

Buksan ang **Grafana → Explore → Loki**, tapos i-type ang mga ito habang nag-de-demo.
Nagbibigay sila ng magandang "live" effect. Palitan ang time range sa **Last 5 minutes**.

## Basics

```logql
# Lahat ng request mula sa demo app
{job="webapp"}

# I-parse ang JSON para makita ang mga field
{job="webapp"} | json

# Readable na format ng bawat linya
{job="webapp"} | json | line_format "{{.method}} {{.path}} -> {{.status}} ip={{.ip}}"
```

## Filter by method / status / path

```logql
# POST requests lang
{job="webapp"} | json | method="POST"

# Mga error lang (4xx/5xx)
{job="webapp"} | json | status >= 400

# Sinong nag-probe sa /admin?
{job="webapp"} | json | path =~ "/admin.*"

# Isang partikular na IP
{job="webapp"} | json | ip="192.168.1.50"
```

## Metrics (para sa graphs / alerts)

```logql
# Requests per method kada minuto
sum by (method) (count_over_time({job="webapp"} [1m]))

# Rate ng errors
sum(rate({job="webapp"} | json | status >= 400 [1m]))

# Top 10 na IP ayon sa dami ng request
topk(10, sum by (ip) (count_over_time({job="webapp"} | json [5m])))

# Request rate per IP — pang-detect ng "sobrang daldal" na kliyente
sum by (ip) (rate({job="webapp"} | json [1m]))
```

## Mga "kahina-hinalang" pattern na pwedeng ipakita

```logql
# Maraming 404 mula sa iisang IP = posibleng scanning/enumeration
topk(5, sum by (ip) (count_over_time({job="webapp"} | json | status=404 [5m])))

# DELETE o PUT sa sensitive path
{job="webapp"} | json | method=~"DELETE|PUT" | path=~"/admin.*"

# Maraming POST /login mula sa iisang IP = posibleng brute force
sum by (ip) (count_over_time({job="webapp"} | json | path="/login" | method="POST" [2m]))
```

> Punto para sa talk: ang mga query na ito ang ginagawa ng isang **SOC analyst** —
> hindi lang basta "may log", kundi tinatanong: sino, ano, gaano kadalas, at bakit kakaiba.
