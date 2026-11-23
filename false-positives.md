# False Positives — paano maagapan bilang monitoring analyst

Ang pinakamahirap na bahagi ng monitoring ay HINDI ang makakita ng aktibidad — kundi ang
malaman kung alin ang **totoong banta** at alin ang **ingay (false positive)**. Ito ang
pupuntahan mo sa defense segment pagkatapos ipakita ang live dashboard.

## Ano ang false positive?

Isang alerto na mukhang atake pero **normal** pala. Halimbawa:
- Isang user na mabilis mag-click → mukhang "brute force" pero tao lang na naiinip.
- Health-check / monitoring bot na laging tumatama sa `/` → mukhang "scanner".
- Deploy o load test → biglang pagtaas ng traffic.
- Mobile app na nag-re-retry dahil mahina ang signal → maraming paulit-ulit na request.

Masama ang sobrang false positives: **alert fatigue** — nasasanay ang analyst na i-ignore
ang alerts, kaya kapag totoo na ang atake, hindi na napapansin.

## Framework: paano magdesisyon (gamit ang dashboard)

Para sa bawat kahina-hinalang bagay, tanungin:

1. **Sino?** (IP / user) — kilala ba? internal? known bot? bagong IP?
2. **Ano?** (method + path) — read-only (GET) ba o may binabago (POST/PUT/DELETE)?
   sensitive path ba (`/admin`, `/login`)?
3. **Gaano kadalas / kabilis?** — tao-level ba o machine-level na rate?
4. **Ano ang resulta?** — 200 (nagtagumpay) ba o puro 401/403/404 (napigilan/nagha-hanap)?
5. **May pattern ba sa oras?** — 3am burst? tuwing deploy? random?

## Mga paraan para bawasan ang false positives

### 1. Mag-baseline muna
Bago mag-alerto, alamin kung ano ang "normal". Patakbuhin ang dashboard ng ilang araw.
Alin ang karaniwang IP, method mix, request rate? Ang alerto ay dapsa **paglihis** dito,
hindi sa absolute number lang.

### 2. Allowlist ng kilalang mabait
Ilista ang known health-checkers, monitoring, internal CIDR. I-exclude sa LogQL:

```logql
{job="webapp"} | json | ip != "10.0.0.5" | status=404
```

### 3. Gumamit ng threshold + duration, hindi single event
Huwag mag-alerto sa isang 404. Mag-alerto kung **>20 na 404 sa loob ng 1 min galing sa
iisang IP** — iyon ang hugis ng scanning, hindi ng tao.

```logql
sum by (ip) (count_over_time({job="webapp"} | json | status=404 [1m])) > 20
```

### 4. I-correlate ang signals
Isang signal = mahina. Pinagsamang signal = malakas:
- Maraming 404 **AT** mula sa bagong IP **AT** may sunod na POST sa `/login` = mas kapani-paniwala.
- Isang 404 lang = malamang typo.

### 5. Tiered severity
- **Info**: kakaiba pero benign (bagong user-agent).
- **Warning**: dapat tingnan (pagtaas ng 403 sa `/admin`).
- **Critical**: aksyon agad (DELETE sa admin na nagtagumpay + 200).

### 6. Suppression / dedup windows
Kung alam mong may deploy mamaya, i-silence muna ang alerts para doon. Mag-dedup ng
paulit-ulit na alerto (isang notification kada 5 min, hindi 500).

### 7. Feedback loop
Tuwing ma-dismiss mo ang isang alerto bilang false positive, i-adjust ang rule.
Ang goal: bumababa ang noise sa paglipas ng panahon, hindi tumataas.

## Demo talking point

> "Ang monitoring ay hindi tungkol sa pagkakaroon ng maraming alerto. Tungkol ito sa
> **pagkakaroon ng TAMANG alerto.** Ang mahusay na analyst ay marunong mag-tune — para
> kapag tumunog ang alarm, pinaniniwalaan ito. Ang isang monitoring na puro false positive
> ay kasing-delikado ng walang monitoring — dahil nawawalan ng tiwala ang tao dito."

## Quick checklist para sa live demo

- [ ] Ipakita ang normal na traffic (audience clicks) — ito ang baseline.
- [ ] Mag-trigger ng "scan" (pindutin nang paulit-ulit ang 404 button) → ipakita ang spike.
- [ ] Ipaliwanag bakit **hindi** agad critical — maaaring isang curious na user lang.
- [ ] Ipakita paano i-filter ang known-good IP → bumaba ang noise.
- [ ] I-correlate: 404 spike + POST /login mula sa iisang IP → ngayon worth investigating.
