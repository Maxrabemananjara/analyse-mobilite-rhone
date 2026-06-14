from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "data" / "powerbi"
OUT = ROOT / "analysis"
OUT.mkdir(exist_ok=True)


def read_csv(name: str):
    with (PBI / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def fnum(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def inum(value: str) -> int:
    if value is None or value == "":
        return 0
    return int(float(str(value).replace(",", ".")))


def mean(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    xbar = sum(x for x, _ in pairs) / len(pairs)
    ybar = sum(y for _, y in pairs) / len(pairs)
    num = sum((x - xbar) * (y - ybar) for x, y in pairs)
    denx = math.sqrt(sum((x - xbar) ** 2 for x, _ in pairs))
    deny = math.sqrt(sum((y - ybar) ** 2 for _, y in pairs))
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def pct(part, total):
    return round(part / total * 100, 2) if total else 0


def top(counter, n=10):
    return [{"key": key, "value": value} for key, value in counter.most_common(n)]


def main():
    trajets = read_csv("fact_trajets.csv")
    date_depart = {r["date_depart_id"]: r for r in read_csv("dim_date_depart.csv")}
    date_arrivee = {r["date_arrivee_id"]: r for r in read_csv("dim_date_arrivee.csv")}
    jour_depart = {r["jour_semaine_depart_id"]: r for r in read_csv("dim_jour_semaine_depart.csv")}
    jour_arrivee = {r["jour_semaine_arrivee_id"]: r for r in read_csv("dim_jour_semaine_arrivee.csv")}
    tranche_depart = {r["tranche_depart_id"]: r for r in read_csv("dim_tranche_depart.csv")}
    tranche_arrivee = {r["tranche_arrivee_id"]: r for r in read_csv("dim_tranche_arrivee.csv")}
    meteo = read_csv("fact_meteo_jour.csv")
    stations = read_csv("fact_stations_taxi.csv")
    ch_bridge = read_csv("bridge_chantier_date_commune.csv")
    comptages = read_csv("fact_comptages.csv")
    dim_channel = {r["channel_id"]: r for r in read_csv("dim_channel_comptage.csv")}

    total_rows = len(trajets)
    distinct_journeys = len({r["journey_id"] for r in trajets})
    distances = [fnum(r["distance_km"]) for r in trajets]
    durations = [fnum(r["duree_min"]) for r in trajets]
    revenues = [fnum(r["revenu_estime_eur"]) for r in trajets]

    by_month = Counter(date_depart[r["date_depart_id"]]["mois_libelle"] for r in trajets)
    by_day_depart = Counter(jour_depart[r["jour_semaine_depart_id"]]["jour_semaine_libelle"] for r in trajets)
    by_day_arrivee = Counter(jour_arrivee[r["jour_semaine_arrivee_id"]]["jour_semaine_libelle"] for r in trajets)
    by_tranche_depart = Counter(tranche_depart[r["tranche_depart_id"]]["tranche_horaire_libelle"] for r in trajets)
    by_tranche_arrivee = Counter(tranche_arrivee[r["tranche_arrivee_id"]]["tranche_horaire_libelle"] for r in trajets)
    heat_depart = Counter((jour_depart[r["jour_semaine_depart_id"]]["jour_semaine_libelle"], tranche_depart[r["tranche_depart_id"]]["tranche_horaire_libelle"]) for r in trajets)
    heat_arrivee = Counter((jour_arrivee[r["jour_semaine_arrivee_id"]]["jour_semaine_libelle"], tranche_arrivee[r["tranche_arrivee_id"]]["tranche_horaire_libelle"]) for r in trajets)

    dep_communes = Counter(r["commune_depart"] for r in trajets)
    arr_communes = Counter(r["commune_arrivee"] for r in trajets)
    dep_communes_mdl = Counter(r["commune_depart"] for r in trajets if r["groupe_commune_depart"] == "Métropole de Lyon")
    arr_communes_mdl = Counter(r["commune_arrivee"] for r in trajets if r["groupe_commune_arrivee"] == "Métropole de Lyon")
    od = Counter((r["commune_depart"], r["commune_arrivee"]) for r in trajets)

    net_commune = {}
    for commune in set(dep_communes_mdl) | set(arr_communes_mdl):
        net_commune[commune] = dep_communes_mdl[commune] - arr_communes_mdl[commune]

    # Profitability by commune and OD
    rev_by_od = defaultdict(list)
    dist_by_od = defaultdict(list)
    dur_by_od = defaultdict(list)
    rev_by_dep = defaultdict(list)
    for r in trajets:
        key = (r["commune_depart"], r["commune_arrivee"])
        rev_by_od[key].append(fnum(r["revenu_estime_eur"]))
        dist_by_od[key].append(fnum(r["distance_km"]))
        dur_by_od[key].append(fnum(r["duree_min"]))
        rev_by_dep[r["commune_depart"]].append(fnum(r["revenu_estime_eur"]))

    od_profit = []
    for key, vals in rev_by_od.items():
        count = len(vals)
        if count >= 50:
            avg_rev = mean(vals)
            avg_dist = mean(dist_by_od[key])
            avg_dur = mean(dur_by_od[key])
            od_profit.append(
                {
                    "od": f"{key[0]} -> {key[1]}",
                    "trajets": count,
                    "revenu_moyen": round(avg_rev, 2),
                    "distance_moyenne_km": round(avg_dist, 2),
                    "duree_moyenne_min": round(avg_dur, 2),
                    "revenu_total": round(sum(v for v in vals if v is not None), 2),
                }
            )
    od_profit_top_avg = sorted(od_profit, key=lambda x: x["revenu_moyen"], reverse=True)[:10]
    od_profit_top_total = sorted(od_profit, key=lambda x: x["revenu_total"], reverse=True)[:10]

    # Weather: choose Lyon-Bron as main station.
    meteo_bron = {r["date_id"]: r for r in meteo if r["nom_station"] == "LYON-BRON"}
    daily_trips = Counter(r["date_depart_id"] for r in trajets)
    weather_rows = []
    for date_id, trips in daily_trips.items():
        m = meteo_bron.get(date_id)
        if not m:
            continue
        rr = fnum(m.get("rr"))
        tm = fnum(m.get("tm"))
        tn = fnum(m.get("tn"))
        tx = fnum(m.get("tx"))
        fxy = fnum(m.get("fxy"))
        weather_rows.append({"date_id": date_id, "trajets": trips, "rr": rr, "tm": tm, "tn": tn, "tx": tx, "fxy": fxy})

    rainy = [r for r in weather_rows if (r["rr"] or 0) > 0]
    dry = [r for r in weather_rows if (r["rr"] or 0) == 0]
    cold = [r for r in weather_rows if r["tm"] is not None and r["tm"] < 5]
    mild = [r for r in weather_rows if r["tm"] is not None and r["tm"] >= 5]
    weather_corr = {
        "pluie_rr_vs_trajets": pearson([r["rr"] for r in weather_rows], [r["trajets"] for r in weather_rows]),
        "temperature_moyenne_vs_trajets": pearson([r["tm"] for r in weather_rows], [r["trajets"] for r in weather_rows]),
        "vent_rafale_fxy_vs_trajets": pearson([r["fxy"] for r in weather_rows], [r["trajets"] for r in weather_rows]),
        "nb_jours_avec_meteo_bron": len(weather_rows),
        "trajets_moyen_jour_pluie": mean([r["trajets"] for r in rainy]),
        "trajets_moyen_jour_sec": mean([r["trajets"] for r in dry]),
        "nb_jours_pluie": len(rainy),
        "nb_jours_secs": len(dry),
        "trajets_moyen_jour_froid_tm_lt_5": mean([r["trajets"] for r in cold]),
        "trajets_moyen_jour_tm_gte_5": mean([r["trajets"] for r in mild]),
        "nb_jours_froids": len(cold),
    }

    # Works: active works by date/commune.
    active_work = defaultdict(int)
    for r in ch_bridge:
        active_work[(r["date_id"], r["commune_id"])] += 1
    with_work = []
    without_work = []
    for r in trajets:
        has_work = active_work.get((r["date_depart_id"], r["commune_depart_id"]), 0) > 0
        payload = {"duration": fnum(r["duree_min"]), "distance": fnum(r["distance_km"]), "revenue": fnum(r["revenu_estime_eur"])}
        if has_work:
            with_work.append(payload)
        else:
            without_work.append(payload)
    work_by_commune = Counter()
    for (date_id, commune_id), n in active_work.items():
        work_by_commune[commune_id] += n

    # Taxi coverage within Metropole de Lyon departure demand.
    station_counts = Counter()
    station_slots = Counter()
    for r in stations:
        commune_id = r["commune_id"]
        station_counts[commune_id] += 1
        station_slots[commune_id] += inum(r["nb_emplacements"])
    dep_by_commune_id_mdl = Counter(r["commune_depart_id"] for r in trajets if r["groupe_commune_depart"] == "Métropole de Lyon")
    commune_name_by_id = {}
    for r in trajets:
        commune_name_by_id[r["commune_depart_id"]] = r["commune_depart"]
        commune_name_by_id[r["commune_arrivee_id"]] = r["commune_arrivee"]
    coverage = []
    for commune_id, trips in dep_by_commune_id_mdl.items():
        slots = station_slots[commune_id]
        coverage.append(
            {
                "commune": commune_name_by_id.get(commune_id, commune_id),
                "trajets_depart": trips,
                "stations": station_counts[commune_id],
                "emplacements": slots,
                "trajets_par_emplacement": round(trips / slots, 2) if slots else None,
            }
        )
    coverage_no_station = sorted([r for r in coverage if r["emplacements"] == 0], key=lambda x: x["trajets_depart"], reverse=True)[:15]
    coverage_pressure = sorted([r for r in coverage if r["emplacements"]], key=lambda x: x["trajets_par_emplacement"], reverse=True)[:15]

    # Comptages, by mobility type and tranche.
    count_by_mobility = Counter()
    count_by_tranche = Counter()
    for r in comptages:
        count = inum(r["count"])
        mobility = dim_channel.get(r["channel_id"], {}).get("mobility_type", "") or "Non renseigne"
        count_by_mobility[mobility] += count
        count_by_tranche[r["tranche_horaire_id"]] += count

    result = {
        "vue_ensemble": {
            "lignes_fact_trajets": total_rows,
            "journey_id_distincts": distinct_journeys,
            "distance_moyenne_km": round(mean(distances), 2),
            "distance_mediane_km": round(median(distances), 2),
            "duree_moyenne_min": round(mean(durations), 2),
            "duree_mediane_min": round(median(durations), 2),
            "revenu_moyen_estime_eur": round(mean(revenues), 2),
            "revenu_median_estime_eur": round(median(revenues), 2),
            "revenu_total_estime_eur": round(sum(v for v in revenues if v is not None), 2),
            "par_mois": dict(by_month),
        },
        "demande_temporelle": {
            "depart_par_jour": top(by_day_depart, 7),
            "depart_par_tranche": top(by_tranche_depart, 6),
            "arrivee_par_jour": top(by_day_arrivee, 7),
            "arrivee_par_tranche": top(by_tranche_arrivee, 6),
            "top_heatmap_depart": [{"jour": k[0], "tranche": k[1], "trajets": v} for k, v in heat_depart.most_common(12)],
            "top_heatmap_arrivee": [{"jour": k[0], "tranche": k[1], "trajets": v} for k, v in heat_arrivee.most_common(12)],
        },
        "demande_geographique": {
            "top_depart_global": top(dep_communes, 15),
            "top_arrivee_global": top(arr_communes, 15),
            "top_depart_metropole_lyon": top(dep_communes_mdl, 15),
            "top_arrivee_metropole_lyon": top(arr_communes_mdl, 15),
            "communes_excedent_depart": sorted([{"commune": k, "depart_moins_arrivee": v} for k, v in net_commune.items()], key=lambda x: x["depart_moins_arrivee"], reverse=True)[:15],
            "communes_excedent_arrivee": sorted([{"commune": k, "arrivee_moins_depart": -v} for k, v in net_commune.items()], key=lambda x: x["arrivee_moins_depart"], reverse=True)[:15],
        },
        "origine_destination": {
            "top_od": [{"od": f"{k[0]} -> {k[1]}", "trajets": v} for k, v in od.most_common(20)],
        },
        "rentabilite": {
            "top_od_revenu_moyen_min_50_trajets": od_profit_top_avg,
            "top_od_revenu_total_min_50_trajets": od_profit_top_total,
            "top_communes_depart_revenu_moyen_min_200_trajets": sorted(
                [
                    {"commune": k, "trajets": len(vals), "revenu_moyen": round(mean(vals), 2), "revenu_total": round(sum(v for v in vals if v is not None), 2)}
                    for k, vals in rev_by_dep.items()
                    if len(vals) >= 200
                ],
                key=lambda x: x["revenu_moyen"],
                reverse=True,
            )[:15],
        },
        "meteo": weather_corr,
        "travaux": {
            "trajets_depart_avec_chantier_commune_jour": len(with_work),
            "trajets_depart_sans_chantier_commune_jour": len(without_work),
            "duree_moyenne_avec_chantier": round(mean([r["duration"] for r in with_work]), 2),
            "duree_moyenne_sans_chantier": round(mean([r["duration"] for r in without_work]), 2),
            "distance_moyenne_avec_chantier": round(mean([r["distance"] for r in with_work]), 2),
            "distance_moyenne_sans_chantier": round(mean([r["distance"] for r in without_work]), 2),
            "revenu_moyen_avec_chantier": round(mean([r["revenue"] for r in with_work]), 2),
            "revenu_moyen_sans_chantier": round(mean([r["revenue"] for r in without_work]), 2),
            "top_communes_jours_chantiers_actifs": top(work_by_commune, 15),
        },
        "offre_taxi": {
            "top_communes_sans_station_par_demande_depart_mdl": coverage_no_station,
            "top_pression_trajets_par_emplacement": coverage_pressure,
        },
        "comptages": {
            "volume_par_mobility_type": top(count_by_mobility, 10),
            "volume_par_tranche_horaire_id": dict(count_by_tranche),
        },
    }

    (OUT / "analyse_reponses_questions.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
