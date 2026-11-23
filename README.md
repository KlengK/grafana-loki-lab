# Grafana + Loki Monitoring Lab

A live log-monitoring demo you can run on one laptop. The audience opens a small
website on their phones and taps buttons. Every request appears within seconds on a
Grafana dashboard: method, path, status code, IP address and browser.

Built for the workshop "Cybersecurity Friend or Foe?" (Module 6: monitoring and
false positives).

```
Audience phone -> demo website (:8080) -> logs/access.log -> Promtail -> Loki (:3100) -> Grafana (:3000)
```

| Part | What it does |
|------|--------------|
| `webapp/` | Flask website with GET, POST, PUT and DELETE buttons, a protected `/admin` page (403), a broken link (404) and a practice login (401). Writes one JSON line per request to `logs/access.log`. |
| `promtail/` | Reads `logs/access.log` and sends each new line to Loki. |
| `loki/` | Stores the log lines and answers LogQL queries. |
| `grafana/` | Loads the Loki data source and the **HTTP Activity Monitor** dashboard automatically. |

## Quick start

You need [Docker Desktop](https://docs.docker.com/get-docker/) (Windows or macOS) or
Docker Engine with the Compose plugin (Linux).

```bash
git clone https://github.com/KlengK/grafana-loki-lab.git
cd grafana-loki-lab
docker compose up -d --build
```

1. Change `GF_SECURITY_ADMIN_PASSWORD` in `docker-compose.yml` before a real event.
2. Open <http://localhost:3000>, sign in as `admin`, and open **Dashboards > HTTP Activity Monitor**.
3. Open <http://localhost:8080> and tap a few buttons. The dashboard updates every 5 seconds.
4. For the audience: find the laptop's IP address (`ipconfig` on Windows, `ip a` on Linux)
   and share `http://<laptop-IP>:8080`. Phones must be on the same Wi-Fi.

Grafana and Loki listen on `127.0.0.1` only, so people on the Wi-Fi can reach the website
but not your dashboard or your log store.

## Real visitor IP addresses on Windows and macOS

Docker Desktop replaces every visitor's address with one internal address, so all phones
look like one IP. Docker Engine on Linux keeps the real addresses. On Windows or macOS,
run the website with Python instead of Docker (Promtail, Loki and Grafana stay in Docker
and read the same `logs` folder):

```powershell
pip install -r webapp/requirements.txt
docker compose stop webapp
$env:PORT = "8080"; $env:LOG_DIR = "logs"; python webapp\app.py
```

On macOS or Linux: `PORT=8080 LOG_DIR=logs python3 webapp/app.py`. Allow Python through the
firewall on private networks when asked.

## Stop and reset

```bash
docker compose down       # stop; keeps stored logs and dashboards
docker compose down -v    # stop and delete stored logs and Grafana data
```

Delete `logs/access.log` as well to start from zero.

## More

- [`LOGQL-CHEATSHEET.md`](LOGQL-CHEATSHEET.md): queries to type live in Grafana Explore (Taglish).
- [`false-positives.md`](false-positives.md): how an analyst tells real attacks from noise (Taglish).

## Notes

- Promtail reached end of life on 2 March 2026; Grafana Alloy replaces it. The pinned
  version 3.1.1 still works for a short offline demo.
- Privacy: the site uses plain HTTP and logs each visitor's IP address and user agent on
  the presenter's laptop. Tell the audience before they connect, and delete the logs after.
  The practice login never sends what is typed.
- Use it only on a network you control, with the consent of the people who connect.
