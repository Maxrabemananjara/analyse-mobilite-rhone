from __future__ import annotations

import csv
import json
import re
import urllib.request
from collections import OrderedDict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data" / "powerbi"
OUT.mkdir(parents=True, exist_ok=True)

START_DATE = date(2026, 1, 1)
END_DATE_EXCLUSIVE = date(2026, 4, 1)

RPC_PATH = PROCESSED / "rpc_trajets_covoiturage_metropole_lyon_2026_01_03.csv"
CHANTIERS_PATH = PROCESSED / "chantiers_perturbants_jan_mar_2026.csv"
METEO_PATH = PROCESSED / "meteo_rr_t_vent_jan_mar_2026.csv"
TARIFS_PATH = PROCESSED / "tarifs_taxi_rhone_2026_reference.csv"

URL_STATIONS_TAXI = (
    "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?"
    "SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename="
    "metropole-de-lyon:pvo_patrimoine_voirie.pvostationtaxi"
    "&outputFormat=CSV&SRSNAME=EPSG:4326"
)
URL_COMPTAGE_SITES = (
    "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?"
    "SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename="
    "metropole-de-lyon:pvo_patrimoine_voirie.pvocomptagesite"
    "&outputFormat=CSV&SRSNAME=EPSG:4326"
)
URL_COMPTAGE_CHANNELS = (
    "https://download.data.grandlyon.com/ws/rdata/"
    "pvo_patrimoine_voirie.pvocomptagechannel/all.csv?maxfeatures=100000&start=1"
)
URL_COMPTAGE_MESURES = (
    "https://download.data.grandlyon.com/ws/timeseries/"
    "pvo_patrimoine_voirie.pvocomptagemeasure/all.json"
)

JOURS = [
    (1, "Lundi"),
    (2, "Mardi"),
    (3, "Mercredi"),
    (4, "Jeudi"),
    (5, "Vendredi"),
    (6, "Samedi"),
    (7, "Dimanche"),
]

MOIS = {
    1: "Janvier",
    2: "Fevrier",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Aout",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Decembre",
}

TRANCHES = [
    (1, "00h-04h", 0, 4),
    (2, "04h-08h", 4, 8),
    (3, "08h-12h", 8, 12),
    (4, "12h-16h", 12, 16),
    (5, "16h-20h", 16, 20),
    (6, "20h-00h", 20, 24),
]

JOURS_FERIES = {date(2026, 1, 1)}

MANIFEST: dict[str, Any] = {"tables": OrderedDict(), "notes": []}


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "mobilite-rhone-powerbi-export/1.0"})
    with urllib.request.urlopen(req, timeout=240) as response:
        return response.read().decode("utf-8-sig")


def read_csv_path(path: Path, delimiter: str = ";") -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def read_csv_url(url: str, delimiter: str = ",") -> list[dict[str, str]]:
    content = request_text(url)
    return list(csv.DictReader(content.splitlines(), delimiter=delimiter))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field, "")) for field in fields})
    MANIFEST["tables"][path.name] = {"rows": len(rows), "columns": len(fields), "fields": fields}


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return text.replace(".", ",")
    text = str(value).strip()
    if is_simple_decimal(text):
        return text.replace(".", ",")
    return text


def is_simple_decimal(text: str) -> bool:
    return bool(re.fullmatch(r"-?\d+\.\d+", text))


def parse_local_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)


def date_id(d: date) -> int:
    return int(d.strftime("%Y%m%d"))


def commune_id(code_insee: str) -> str:
    code = (code_insee or "").strip()
    return f"INSEE_{code}" if code else ""


def station_meteo_id(num_poste: str) -> str:
    value = (num_poste or "").strip()
    return f"MF_{value}" if value else ""


def tranche_id_from_hour(hour: int) -> int:
    if 0 <= hour < 4:
        return 1
    if 4 <= hour < 8:
        return 2
    if 8 <= hour < 12:
        return 3
    if 12 <= hour < 16:
        return 4
    if 16 <= hour < 20:
        return 5
    return 6


def parse_wkt_point(value: str) -> tuple[str, str]:
    match = re.match(r"POINT \(([-0-9.]+) ([-0-9.]+)\)", value or "")
    if not match:
        return "", ""
    lon, lat = match.group(1), match.group(2)
    return lon, lat


def parse_date(value: str) -> date:
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def daterange(start: date, end_exclusive: date):
    current = start
    while current < end_exclusive:
        yield current
        current += timedelta(days=1)


def normalize_bool(value: str) -> str:
    text = (value or "").strip().lower()
    if text in {"true", "1", "oui", "yes"}:
        return "1"
    if text in {"false", "0", "non", "no"}:
        return "0"
    return ""


def build_date_rows(key_name: str, dates: list[date]) -> tuple[list[dict[str, Any]], list[str]]:
    fields = [
        key_name,
        "date",
        "annee",
        "trimestre",
        "mois_numero",
        "mois_libelle",
        "jour_mois",
        "jour_semaine_id",
        "jour_semaine_libelle",
        "ordre_jour",
        "weekend_flag",
    ]
    rows = []
    for d in dates:
        jour_id = d.isoweekday()
        rows.append(
            {
                key_name: date_id(d),
                "date": d.isoformat(),
                "annee": d.year,
                "trimestre": ((d.month - 1) // 3) + 1,
                "mois_numero": d.month,
                "mois_libelle": MOIS[d.month],
                "jour_mois": d.day,
                "jour_semaine_id": jour_id,
                "jour_semaine_libelle": JOURS[jour_id - 1][1],
                "ordre_jour": jour_id,
                "weekend_flag": 1 if jour_id in (6, 7) else 0,
            }
        )
    return rows, fields


def build_jour_rows(key_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    fields = [key_name, "jour_semaine_libelle", "ordre_jour"]
    return [{key_name: jid, "jour_semaine_libelle": label, "ordre_jour": jid} for jid, label in JOURS], fields


def build_tranche_rows(key_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    fields = [key_name, "tranche_horaire_libelle", "heure_debut", "heure_fin", "ordre_tranche"]
    rows = [
        {
            key_name: tid,
            "tranche_horaire_libelle": label,
            "heure_debut": start,
            "heure_fin": end,
            "ordre_tranche": tid,
        }
        for tid, label, start, end in TRANCHES
    ]
    return rows, fields


def add_commune(communes: dict[str, dict[str, Any]], code: str, nom: str = "", group: str = "", dept: str = "", country: str = "", source: str = "") -> None:
    if not code:
        return
    cid = commune_id(code)
    current = communes.setdefault(
        cid,
        {
            "commune_id": cid,
            "code_insee": code,
            "commune_nom": "",
            "groupe_commune": "",
            "departement": "",
            "pays": "",
            "sources": set(),
        },
    )
    if nom and not current["commune_nom"]:
        current["commune_nom"] = nom
    if group and not current["groupe_commune"]:
        current["groupe_commune"] = group
    if dept and not current["departement"]:
        current["departement"] = dept
    if country and not current["pays"]:
        current["pays"] = country
    if source:
        current["sources"].add(source)


def build_commune_rows(communes: dict[str, dict[str, Any]], key_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    fields = [key_name, "code_insee", "commune_nom", "groupe_commune", "departement", "pays", "sources"]
    rows = []
    for cid, row in sorted(communes.items(), key=lambda item: item[0]):
        rows.append(
            {
                key_name: cid,
                "code_insee": row["code_insee"],
                "commune_nom": row["commune_nom"],
                "groupe_commune": row["groupe_commune"],
                "departement": row["departement"],
                "pays": row["pays"],
                "sources": ", ".join(sorted(row["sources"])),
            }
        )
    return rows, fields


def load_sources():
    print("[Sources] lecture RPC filtre", flush=True)
    rpc_rows = read_csv_path(RPC_PATH, delimiter=";")
    print("[Sources] lecture chantiers", flush=True)
    chantiers_rows = read_csv_path(CHANTIERS_PATH, delimiter=";")
    print("[Sources] lecture meteo", flush=True)
    meteo_rows = read_csv_path(METEO_PATH, delimiter=";")
    print("[Sources] lecture tarifs", flush=True)
    tarifs_rows = read_csv_path(TARIFS_PATH, delimiter=";")
    print("[Sources] telechargement stations taxi", flush=True)
    stations_rows = read_csv_url(URL_STATIONS_TAXI, delimiter=",")
    print("[Sources] telechargement sites de comptage", flush=True)
    sites_rows = read_csv_url(URL_COMPTAGE_SITES, delimiter=",")
    print("[Sources] telechargement channels de comptage", flush=True)
    channels_rows = read_csv_url(URL_COMPTAGE_CHANNELS, delimiter=";")
    return rpc_rows, chantiers_rows, meteo_rows, tarifs_rows, stations_rows, sites_rows, channels_rows


def build_fact_trajets(rpc_rows: list[dict[str, str]], tarifs_by_id: dict[str, dict[str, str]]):
    rows: list[dict[str, Any]] = []
    excluded_outside_period = 0
    seen_journey_ids: dict[str, int] = {}
    for index, row in enumerate(rpc_rows, start=1):
        start_dt = parse_local_datetime(row["journey_start_datetime"])
        if not (START_DATE <= start_dt.date() < END_DATE_EXCLUSIVE):
            excluded_outside_period += 1
            continue

        duration_min = int(float(row["journey_duration"]))
        arrival_dt = start_dt + timedelta(minutes=duration_min)
        start_day_id = start_dt.isoweekday()
        arrival_day_id = arrival_dt.isoweekday()
        start_tranche_id = tranche_id_from_hour(start_dt.hour)
        arrival_tranche_id = tranche_id_from_hour(arrival_dt.hour)
        distance_m = int(float(row["journey_distance"]))
        distance_km = distance_m / 1000

        night_or_special = start_dt.hour < 7 or start_dt.hour >= 19 or start_day_id == 7 or start_dt.date() in JOURS_FERIES
        tarif_id = "B" if night_or_special else "A"
        tarif = tarifs_by_id.get(tarif_id, {})
        price_km = float((tarif.get("prix_km_eur") or "0").replace(",", "."))
        prise = float((tarif.get("prise_en_charge_eur") or "0").replace(",", "."))
        minimum = float((tarif.get("course_minimum_eur") or "0").replace(",", "."))
        revenu = max(minimum, prise + distance_km * price_km)

        journey_id = row["journey_id"]
        duplicate_rank = seen_journey_ids.get(journey_id, 0) + 1
        seen_journey_ids[journey_id] = duplicate_rank

        rows.append(
            {
                "trajet_ligne_id": index,
                "journey_id": journey_id,
                "journey_id_occurrence": duplicate_rank,
                "trip_id": row["trip_id"],
                "date_depart_id": date_id(start_dt.date()),
                "date_arrivee_id": date_id(arrival_dt.date()),
                "jour_semaine_depart_id": start_day_id,
                "jour_semaine_arrivee_id": arrival_day_id,
                "tranche_depart_id": start_tranche_id,
                "tranche_arrivee_id": arrival_tranche_id,
                "commune_depart_id": commune_id(row["journey_start_insee"]),
                "commune_arrivee_id": commune_id(row["journey_end_insee"]),
                "tarif_id_estime": tarif_id,
                "date_heure_depart": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "date_heure_arrivee_estimee": arrival_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "date_depart_source": row["journey_start_date"],
                "heure_depart_source": row["journey_start_time"],
                "date_arrivee_source": row["journey_end_date"],
                "heure_arrivee_source": row["journey_end_time"],
                "date_heure_arrivee_source": row["journey_end_datetime"],
                "longitude_depart": row["journey_start_lon"],
                "latitude_depart": row["journey_start_lat"],
                "code_insee_depart": row["journey_start_insee"],
                "departement_depart": row["journey_start_department"],
                "commune_depart": row["journey_start_town"],
                "groupe_commune_depart": row["journey_start_towngroup"],
                "pays_depart": row["journey_start_country"],
                "longitude_arrivee": row["journey_end_lon"],
                "latitude_arrivee": row["journey_end_lat"],
                "code_insee_arrivee": row["journey_end_insee"],
                "departement_arrivee": row["journey_end_department"],
                "commune_arrivee": row["journey_end_town"],
                "groupe_commune_arrivee": row["journey_end_towngroup"],
                "pays_arrivee": row["journey_end_country"],
                "places_passager": row["passenger_seats"],
                "classe_operateur": row["operator_class"],
                "distance_m": distance_m,
                "distance_km": round(distance_km, 3),
                "duree_min": duration_min,
                "incitation_flag": 1 if row["has_incentive"].strip().upper() == "OUI" else 0,
                "incitation_libelle": row["has_incentive"],
                "revenu_estime_eur": round(revenu, 2),
                "revenu_estime_scenario": "Tarif A/B selon heure, dimanche et jour ferie, hors attente et supplements",
            }
        )
    fields = list(rows[0].keys()) if rows else []
    MANIFEST["notes"].append(
        f"RPC: {excluded_outside_period} lignes hors periode stricte Janvier-Mars 2026 exclues du modele Power BI, conservees dans le staging."
    )
    MANIFEST["notes"].append(
        "Arrivee trajet: journey_end_datetime source est identique au depart dans le RPC filtre; date_heure_arrivee_estimee = depart local + journey_duration."
    )
    return rows, fields


def build_fact_stations_taxi(stations_rows: list[dict[str, str]]):
    rows = []
    for row in stations_rows:
        lon, lat = parse_wkt_point(row.get("the_geom", ""))
        rows.append(
            {
                "station_taxi_id": f"TAXI_{row.get('gid', '').strip()}",
                "commune_id": commune_id(row.get("insee", "")),
                "fid": row.get("FID", ""),
                "gid": row.get("gid", ""),
                "nom": row.get("nom", ""),
                "adresse": row.get("adresse", ""),
                "commune": row.get("commune", ""),
                "code_insee": row.get("insee", ""),
                "nb_emplacements": row.get("nbemplacement", ""),
                "telephone_flag": normalize_bool(row.get("telephone", "")),
                "separateur_taxi": row.get("separateurtaxi", ""),
                "abri_flag": normalize_bool(row.get("abri", "")),
                "panneau_flag": normalize_bool(row.get("panneau", "")),
                "diodes_flag": normalize_bool(row.get("diodes", "")),
                "totem_flag": normalize_bool(row.get("totem", "")),
                "observation": row.get("observation", ""),
                "validite": row.get("validite", ""),
                "longitude": lon,
                "latitude": lat,
                "geometrie_wkt": row.get("the_geom", ""),
            }
        )
    return rows, list(rows[0].keys()) if rows else []


def build_dim_chantier(chantiers_rows: list[dict[str, str]]):
    rows = []
    for row in chantiers_rows:
        out = {
            "chantier_id": f"CHANTIER_{row.get('gid', '').strip()}",
            "commune_id": commune_id(row.get("insee", "")),
            "fid": row.get("FID", ""),
            "gid": row.get("gid", ""),
            "nom_voie": row.get("nom", ""),
            "nom_chantier": row.get("nomchantier", ""),
            "commune": row.get("commune1", ""),
            "code_insee": row.get("insee", ""),
            "precision_localisation": row.get("precisionlocalisation", ""),
            "debut_chantier": row.get("debutchantier", ""),
            "fin_chantier": row.get("finchantier", ""),
            "description_internet": row.get("descripchantierinternet", ""),
            "avancement": row.get("avancement", ""),
            "importance": row.get("importance", ""),
            "type_perturbation": row.get("typeperturbation", ""),
            "intervenant": row.get("intervenant", ""),
            "validite": row.get("validite", ""),
            "code_importance": row.get("codeimportance", ""),
            "document_joint": row.get("document_joint", ""),
            "url_document": row.get("url_document", ""),
            "geometrie_wkt": row.get("the_geom", ""),
        }
        rows.append(out)
    return rows, list(rows[0].keys()) if rows else []


def build_bridge_chantiers(chantiers_rows: list[dict[str, str]]):
    rows = []
    for row in chantiers_rows:
        chantier_id = f"CHANTIER_{row.get('gid', '').strip()}"
        start = max(parse_date(row["debutchantier"]), START_DATE)
        end = min(parse_date(row["finchantier"]), END_DATE_EXCLUSIVE - timedelta(days=1))
        if start > end:
            continue
        for d in daterange(start, end + timedelta(days=1)):
            rows.append(
                {
                    "chantier_id": chantier_id,
                    "date_id": date_id(d),
                    "commune_id": commune_id(row.get("insee", "")),
                    "chantier_actif_flag": 1,
                    "code_importance": row.get("codeimportance", ""),
                    "importance": row.get("importance", ""),
                    "type_perturbation": row.get("typeperturbation", ""),
                }
            )
    return rows, list(rows[0].keys()) if rows else []


def build_dim_sites(sites_rows: list[dict[str, str]]):
    rows = []
    for row in sites_rows:
        rows.append(
            {
                "site_id": row.get("site_id", ""),
                "commune_id": commune_id(row.get("fr_insee_code", "")),
                "fid": row.get("FID", ""),
                "gid": row.get("gid", ""),
                "parent_site_id": row.get("parent_site_id", ""),
                "code_insee": row.get("fr_insee_code", ""),
                "longitude": row.get("xlong", ""),
                "latitude": row.get("ylat", ""),
                "external_ids": row.get("external_ids", ""),
                "infrastructure_type": row.get("infrastructure_type", ""),
                "geometrie_wkt": row.get("the_geom", ""),
                "site_name": row.get("site_name", ""),
            }
        )
    return rows, list(rows[0].keys()) if rows else []


def build_dim_channels(channels_rows: list[dict[str, str]]):
    rows = []
    for row in channels_rows:
        rows.append(
            {
                "channel_id": row.get("channel_id", ""),
                "channel_provider_id": row.get("channel_provider_id", ""),
                "site_provider_id": row.get("site_provider_id", ""),
                "site_id": row.get("site_id", ""),
                "mobility_type": row.get("mobility_type", ""),
                "commentaire": row.get("comment", ""),
                "counter_transmission_type": row.get("counter_transmission_type", ""),
                "publication_transmission_type": row.get("publication_transmission_type", ""),
                "counter_type": row.get("counter_type", ""),
                "direction": row.get("direction", ""),
                "provider_direction_code": row.get("provider_direction_code", ""),
                "provider_direction_name": row.get("provider_direction_name", ""),
                "data_provider_name": row.get("data_provider_name", ""),
                "temporality": row.get("temporality", ""),
                "started_at": row.get("started_at", ""),
                "ended_at": row.get("ended_at", ""),
                "last_updated_at": row.get("last_updated_at", ""),
                "time_step": row.get("time_step", ""),
                "provider_portal_url": row.get("provider_portal_url", ""),
            }
        )
    return rows, list(rows[0].keys()) if rows else []


def build_fact_comptages(channel_site_by_id: dict[str, str]):
    fields = ["comptage_ligne_id", "channel_id", "site_id", "counter_id", "date_id", "tranche_horaire_id", "start_datetime", "end_datetime", "count"]
    path = OUT / "fact_comptages.csv"
    row_count = 0
    page_size = 100000
    start = 1
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        while True:
            url = (
                f"{URL_COMPTAGE_MESURES}?start_datetime__gte=2026-01-01"
                f"&start_datetime__lt=2026-04-01&maxfeatures={page_size}&start={start}"
            )
            print(f"[Comptages] page start={start}", flush=True)
            req = urllib.request.Request(url, headers={"User-Agent": "mobilite-rhone-powerbi-export/1.0"})
            with urllib.request.urlopen(req, timeout=240) as response:
                payload = json.loads(response.read().decode("utf-8"))
            values = payload.get("values") or []
            for value in values:
                row_count += 1
                start_dt = datetime.strptime(value["start_datetime"][:19], "%Y-%m-%d %H:%M:%S")
                out = {
                    "comptage_ligne_id": row_count,
                    "channel_id": value.get("channel_id", ""),
                    "site_id": channel_site_by_id.get(value.get("channel_id", ""), ""),
                    "counter_id": value.get("counter_id", ""),
                    "date_id": date_id(start_dt.date()),
                    "tranche_horaire_id": tranche_id_from_hour(start_dt.hour),
                    "start_datetime": value.get("start_datetime", ""),
                    "end_datetime": value.get("end_datetime", ""),
                    "count": value.get("count", ""),
                }
                writer.writerow({field: format_value(out.get(field, "")) for field in fields})
            if len(values) < page_size:
                break
            start += page_size
    MANIFEST["tables"][path.name] = {"rows": row_count, "columns": len(fields), "fields": fields}


def build_fact_meteo(meteo_rows: list[dict[str, str]]):
    rows = []
    for row in meteo_rows:
        d = datetime.strptime(row["AAAAMMJJ"], "%Y%m%d").date()
        out = OrderedDict()
        out["station_meteo_id"] = station_meteo_id(row.get("NUM_POSTE", ""))
        out["date_id"] = date_id(d)
        out["date_observation"] = d.isoformat()
        for key, value in row.items():
            normalized = key.lower()
            if normalized == "num_poste":
                out["num_poste_source"] = value
            elif normalized == "nom_usuel":
                out["nom_station"] = value
            elif normalized == "lat":
                out["latitude"] = value
            elif normalized == "lon":
                out["longitude"] = value
            elif normalized == "alti":
                out["altitude_m"] = value
            elif normalized == "aaaammjj":
                out["date_source_aaaammjj"] = value
            else:
                out[normalized] = value
        rows.append(dict(out))
    return rows, list(rows[0].keys()) if rows else []


def build_dim_station_meteo(meteo_rows: list[dict[str, str]]):
    by_station: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for row in meteo_rows:
        sid = station_meteo_id(row.get("NUM_POSTE", ""))
        by_station.setdefault(
            sid,
            {
                "station_meteo_id": sid,
                "num_poste": row.get("NUM_POSTE", ""),
                "nom_station": row.get("NOM_USUEL", ""),
                "latitude": row.get("LAT", ""),
                "longitude": row.get("LON", ""),
                "altitude_m": row.get("ALTI", ""),
            },
        )
    rows = list(by_station.values())
    return rows, list(rows[0].keys()) if rows else []


def build_dim_tarifs(tarifs_rows: list[dict[str, str]]):
    rows = []
    for row in tarifs_rows:
        rows.append(
            {
                "tarif_id": row.get("tarif", ""),
                "tarif_libelle": f"Tarif {row.get('tarif', '')}",
                "periode": row.get("periode", ""),
                "condition_retour": row.get("condition_retour", ""),
                "prix_km_eur": row.get("prix_km_eur", ""),
                "prise_en_charge_eur": row.get("prise_en_charge_eur", ""),
                "course_minimum_eur": row.get("course_minimum_eur", ""),
                "attente_marche_lente_eur_h": row.get("attente_marche_lente_eur_h", ""),
            }
        )
    return rows, list(rows[0].keys()) if rows else []


def collect_communes(rpc_rows, chantiers_rows, stations_rows, sites_rows):
    communes: dict[str, dict[str, Any]] = {}
    for row in rpc_rows:
        add_commune(
            communes,
            row.get("journey_start_insee", ""),
            row.get("journey_start_town", ""),
            row.get("journey_start_towngroup", ""),
            row.get("journey_start_department", ""),
            row.get("journey_start_country", ""),
            "rpc_depart",
        )
        add_commune(
            communes,
            row.get("journey_end_insee", ""),
            row.get("journey_end_town", ""),
            row.get("journey_end_towngroup", ""),
            row.get("journey_end_department", ""),
            row.get("journey_end_country", ""),
            "rpc_arrivee",
        )
    for row in chantiers_rows:
        add_commune(communes, row.get("insee", ""), row.get("commune1", ""), dept=(row.get("insee", "") or "")[:2], country="France", source="chantiers")
    for row in stations_rows:
        add_commune(communes, row.get("insee", ""), row.get("commune", ""), dept=(row.get("insee", "") or "")[:2], country="France", source="stations_taxi")
    for row in sites_rows:
        add_commune(communes, row.get("fr_insee_code", ""), dept=(row.get("fr_insee_code", "") or "")[:2], country="France", source="comptage_sites")
    for value in communes.values():
        if not value["commune_nom"]:
            value["commune_nom"] = value["code_insee"]
    return communes


def write_readme() -> None:
    text = """# Exports Power BI

Parametres des CSV :

- separateur de colonnes : `;`
- separateur decimal : `,`
- encodage : UTF-8 avec BOM
- dates : `AAAA-MM-JJ`
- date-heures : `AAAA-MM-JJ HH:MM:SS`
- latitudes / longitudes : colonnes numeriques separees, decimal comma, compatibles avec Power BI FR

Regles importantes :

- les tables de faits ne sont pas reliees entre elles ;
- les dimensions ne sont pas reliees entre elles ;
- les relations Power BI sont de type dimension `1` vers fact `*` ;
- `fact_trajets` conserve les lignes detaillees, avec un identifiant technique `trajet_ligne_id` ;
- `journey_id` n'est pas utilise comme cle primaire stricte car 5 occurrences sont dupliquees dans le brut ;
- l'arrivee trajet est estimee par `date_heure_depart + duree_min`, car `journey_end_datetime` est identique au depart dans le RPC filtre.

Pour les cartes Power BI :

- utiliser `latitude_depart` / `longitude_depart` ou `latitude_arrivee` / `longitude_arrivee` dans `fact_trajets` ;
- utiliser `latitude` / `longitude` dans `fact_stations_taxi`, `dim_site_comptage` et `dim_station_meteo` ;
- definir la categorie de donnees Power BI sur Latitude et Longitude.
"""
    (OUT / "README_POWERBI.md").write_text(text, encoding="utf-8")


def main() -> int:
    rpc_rows, chantiers_rows, meteo_rows, tarifs_rows, stations_rows, sites_rows, channels_rows = load_sources()
    tarifs_by_id = {row["tarif"]: row for row in tarifs_rows}

    print("[Dimensions] communes", flush=True)
    communes = collect_communes(rpc_rows, chantiers_rows, stations_rows, sites_rows)

    print("[Dimensions] dates, jours, tranches", flush=True)
    date_values = list(daterange(START_DATE, END_DATE_EXCLUSIVE))
    date_rows, date_fields = build_date_rows("date_id", date_values)
    write_csv(OUT / "dim_date.csv", date_rows, date_fields)
    date_depart_rows, date_depart_fields = build_date_rows("date_depart_id", date_values)
    write_csv(OUT / "dim_date_depart.csv", date_depart_rows, date_depart_fields)
    date_arrivee_rows, date_arrivee_fields = build_date_rows("date_arrivee_id", date_values + [END_DATE_EXCLUSIVE])
    write_csv(OUT / "dim_date_arrivee.csv", date_arrivee_rows, date_arrivee_fields)

    for name, key in [
        ("dim_jour_semaine.csv", "jour_semaine_id"),
        ("dim_jour_semaine_depart.csv", "jour_semaine_depart_id"),
        ("dim_jour_semaine_arrivee.csv", "jour_semaine_arrivee_id"),
    ]:
        rows, fields = build_jour_rows(key)
        write_csv(OUT / name, rows, fields)

    for name, key in [
        ("dim_tranche_horaire.csv", "tranche_horaire_id"),
        ("dim_tranche_depart.csv", "tranche_depart_id"),
        ("dim_tranche_arrivee.csv", "tranche_arrivee_id"),
    ]:
        rows, fields = build_tranche_rows(key)
        write_csv(OUT / name, rows, fields)

    for name, key in [
        ("dim_commune.csv", "commune_id"),
        ("dim_commune_depart.csv", "commune_depart_id"),
        ("dim_commune_arrivee.csv", "commune_arrivee_id"),
    ]:
        rows, fields = build_commune_rows(communes, key)
        write_csv(OUT / name, rows, fields)

    print("[Dimensions/Facts] tables reference", flush=True)
    tarif_rows, tarif_fields = build_dim_tarifs(tarifs_rows)
    write_csv(OUT / "dim_tarif_taxi.csv", tarif_rows, tarif_fields)

    station_rows, station_fields = build_fact_stations_taxi(stations_rows)
    write_csv(OUT / "fact_stations_taxi.csv", station_rows, station_fields)

    chantier_rows, chantier_fields = build_dim_chantier(chantiers_rows)
    write_csv(OUT / "dim_chantier.csv", chantier_rows, chantier_fields)

    bridge_rows, bridge_fields = build_bridge_chantiers(chantiers_rows)
    write_csv(OUT / "bridge_chantier_date_commune.csv", bridge_rows, bridge_fields)

    site_rows, site_fields = build_dim_sites(sites_rows)
    write_csv(OUT / "dim_site_comptage.csv", site_rows, site_fields)

    channel_rows, channel_fields = build_dim_channels(channels_rows)
    write_csv(OUT / "dim_channel_comptage.csv", channel_rows, channel_fields)

    station_meteo_rows, station_meteo_fields = build_dim_station_meteo(meteo_rows)
    write_csv(OUT / "dim_station_meteo.csv", station_meteo_rows, station_meteo_fields)

    print("[Fact] trajets", flush=True)
    fact_trajets_rows, fact_trajets_fields = build_fact_trajets(rpc_rows, tarifs_by_id)
    write_csv(OUT / "fact_trajets.csv", fact_trajets_rows, fact_trajets_fields)

    print("[Fact] meteo", flush=True)
    fact_meteo_rows, fact_meteo_fields = build_fact_meteo(meteo_rows)
    write_csv(OUT / "fact_meteo_jour.csv", fact_meteo_rows, fact_meteo_fields)

    print("[Fact] comptages", flush=True)
    channel_site_by_id = {row.get("channel_id", ""): row.get("site_id", "") for row in channels_rows}
    build_fact_comptages(channel_site_by_id)

    write_readme()
    MANIFEST["generated_at"] = datetime.now().isoformat(timespec="seconds")
    (OUT / "manifest_powerbi.json").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Exports Power BI generes dans {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
