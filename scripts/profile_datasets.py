from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis"
DATA_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = date(2026, 1, 1)
END_DATE_EXCLUSIVE = date(2026, 4, 1)

LYON_TOWNGROUP = "Métropole de Lyon"

RPC_MONTHS = {
    "2026-01": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20260202-093213/2026-01.csv",
    "2026-02": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20260302-091739/2026-02.csv",
    "2026-03": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20260409-085423/2026-03.csv",
}

URLS = {
    "stations_taxi": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:pvo_patrimoine_voirie.pvostationtaxi&outputFormat=CSV&SRSNAME=EPSG:4326",
    "chantiers_perturbants": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:pvo_patrimoine_voirie.pvochantierperturbant&outputFormat=CSV&SRSNAME=EPSG:4326",
    "comptage_sites": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:pvo_patrimoine_voirie.pvocomptagesite&outputFormat=CSV&SRSNAME=EPSG:4326",
    "comptage_channels": "https://download.data.grandlyon.com/ws/rdata/pvo_patrimoine_voirie.pvocomptagechannel/all.csv?maxfeatures=100000&start=1",
    "meteo_rr_t_vent": "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/Q_69_latest-2025-2026_RR-T-Vent.csv.gz",
    "meteo_autres": "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/Q_69_latest-2025-2026_autres-parametres.csv.gz",
    "meteo_desc_rr_t_vent": "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/Q_descriptif_champs_RR-T-Vent.csv",
    "meteo_desc_autres": "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/Q_descriptif_champs_autres-parametres.csv",
}

COMPTAGE_MEASURES_URL = (
    "https://download.data.grandlyon.com/ws/timeseries/"
    "pvo_patrimoine_voirie.pvocomptagemeasure/all.json"
)

NA_LITERALS = {"", "na", "n/a", "null", "none", "nan", "nd", "mq", "non renseigne", "non renseigné"}


FIELD_DESCRIPTIONS = {
    "rpc_trajets_covoiturage_lyon": {
        "journey_id": "Identifiant unique du trajet passager-conducteur dans le registre.",
        "trip_id": "Identifiant operateur permettant de regrouper plusieurs passagers dans un meme vehicule.",
        "journey_start_datetime": "Date et heure de depart avec fuseau horaire Paris.",
        "journey_start_date": "Date de depart au format AAAA-MM-JJ.",
        "journey_start_time": "Heure de depart arrondie, au format HH:MM:SS.",
        "journey_start_lon": "Longitude WGS84 du point de prise en charge, arrondie au niveau source.",
        "journey_start_lat": "Latitude WGS84 du point de prise en charge, arrondie au niveau source.",
        "journey_start_insee": "Code INSEE de la commune ou arrondissement de depart.",
        "journey_start_department": "Departement du point de depart.",
        "journey_start_town": "Commune ou arrondissement de depart.",
        "journey_start_towngroup": "EPCI/AOM du point de depart.",
        "journey_start_country": "Pays du point de depart.",
        "journey_end_datetime": "Date et heure d'arrivee avec fuseau horaire Paris.",
        "journey_end_date": "Date d'arrivee au format AAAA-MM-JJ.",
        "journey_end_time": "Heure d'arrivee arrondie, au format HH:MM:SS.",
        "journey_end_lon": "Longitude WGS84 du point de depose, arrondie au niveau source.",
        "journey_end_lat": "Latitude WGS84 du point de depose, arrondie au niveau source.",
        "journey_end_insee": "Code INSEE de la commune ou arrondissement d'arrivee.",
        "journey_end_department": "Departement du point d'arrivee.",
        "journey_end_town": "Commune ou arrondissement d'arrivee.",
        "journey_end_towngroup": "EPCI/AOM du point d'arrivee.",
        "journey_end_country": "Pays du point d'arrivee.",
        "passenger_seats": "Nombre de places reservees par le passager.",
        "operator_class": "Classe de preuve de covoiturage.",
        "journey_distance": "Distance declaree par l'operateur, en metres.",
        "journey_duration": "Duree declaree par l'operateur, arrondie en minutes.",
        "has_incentive": "Indique si le trajet est incite par une campagne ou un operateur.",
    },
    "stations_taxi": {
        "FID": "Identifiant technique WFS.",
        "nom": "Code ou nom court de la station taxi.",
        "adresse": "Adresse de la station.",
        "commune": "Commune de localisation.",
        "insee": "Code INSEE de la commune.",
        "nbemplacement": "Nombre d'emplacements taxi declares.",
        "telephone": "Presence d'un telephone ou information assimilee.",
        "separateurtaxi": "Type de separateur ou marquage de l'emplacement.",
        "abri": "Presence d'un abri.",
        "panneau": "Presence d'un panneau.",
        "diodes": "Presence de diodes lumineuses.",
        "totem": "Presence d'un totem.",
        "observation": "Commentaire libre.",
        "validite": "Statut de validation de l'objet.",
        "gid": "Identifiant numerique Grand Lyon.",
        "the_geom": "Geometrie WKT en WGS84.",
    },
    "chantiers_perturbants": {
        "FID": "Identifiant technique WFS.",
        "nom": "Voie ou axe concerne.",
        "nomchantier": "Nom du chantier.",
        "commune1": "Commune principale concernee.",
        "insee": "Code INSEE de la commune.",
        "precisionlocalisation": "Precision textuelle sur la localisation.",
        "debutchantier": "Date de debut du chantier.",
        "finchantier": "Date de fin prevue du chantier.",
        "descripchantierinternet": "Description publiee sur internet.",
        "avancement": "Etat d'avancement.",
        "importance": "Niveau d'importance ou de perturbation.",
        "typeperturbation": "Nature de la perturbation.",
        "intervenant": "Intervenant ou maitre d'ouvrage.",
        "validite": "Statut de validation.",
        "codeimportance": "Code numerique d'importance.",
        "document_joint": "Reference eventuelle d'un document joint.",
        "url_document": "URL du document joint.",
        "gid": "Identifiant numerique Grand Lyon.",
        "the_geom": "Geometrie WKT en WGS84.",
    },
    "comptage_sites": {
        "FID": "Identifiant technique WFS.",
        "site_id": "Identifiant du site de comptage.",
        "site_provider_id": "Identifiant du site chez le fournisseur.",
        "name": "Nom du site de comptage.",
        "commune": "Commune du site, si renseignee.",
        "insee": "Code INSEE, si renseigne.",
        "the_geom": "Geometrie WKT en WGS84.",
    },
    "comptage_channels": {
        "channel_id": "Identifiant du canal de mesure.",
        "channel_provider_id": "Identifiant du canal chez le fournisseur.",
        "site_provider_id": "Identifiant fournisseur du site rattache.",
        "site_id": "Identifiant du site rattache.",
        "mobility_type": "Type de mobilite mesuree.",
        "comment": "Commentaire libre.",
        "counter_transmission_type": "Mode de transmission du compteur.",
        "publication_transmission_type": "Mode de transmission pour publication.",
        "counter_type": "Type de compteur.",
        "direction": "Direction mesuree.",
        "provider_direction_code": "Code direction chez le fournisseur.",
        "provider_direction_name": "Nom direction chez le fournisseur.",
        "data_provider_name": "Nom du fournisseur de donnees.",
        "temporality": "Temporalite de la mesure.",
        "started_at": "Date de debut de validite du canal.",
        "ended_at": "Date de fin de validite du canal.",
        "last_updated_at": "Date de derniere mise a jour.",
        "time_step": "Pas temporel de mesure, en minutes.",
        "provider_portal_url": "URL source du fournisseur.",
    },
    "comptage_mesures_jan_mar_2026": {
        "channel_id": "Identifiant du canal de mesure.",
        "counter_id": "Identifiant du compteur physique.",
        "start_datetime": "Debut de la fenetre de comptage.",
        "end_datetime": "Fin de la fenetre de comptage.",
        "count": "Nombre de passages comptes sur la fenetre.",
    },
    "meteo_rr_t_vent_jan_mar_2026": {
        "NUM_POSTE": "Identifiant de la station meteorologique.",
        "NOM_USUEL": "Nom usuel de la station.",
        "LAT": "Latitude de la station.",
        "LON": "Longitude de la station.",
        "ALTI": "Altitude de la station.",
        "AAAAMMJJ": "Date d'observation au format AAAAMMJJ.",
        "RR": "Cumul quotidien de precipitations.",
        "TN": "Temperature minimale quotidienne.",
        "TX": "Temperature maximale quotidienne.",
        "TM": "Temperature moyenne quotidienne, si disponible.",
        "FFM": "Vitesse moyenne quotidienne du vent, si disponible.",
        "FXY": "Rafale maximale quotidienne, si disponible.",
    },
    "meteo_autres_jan_mar_2026": {
        "NUM_POSTE": "Identifiant de la station meteorologique.",
        "NOM_USUEL": "Nom usuel de la station.",
        "LAT": "Latitude de la station.",
        "LON": "Longitude de la station.",
        "ALTI": "Altitude de la station.",
        "AAAAMMJJ": "Date d'observation au format AAAAMMJJ.",
    },
    "tarifs_taxi_rhone_2026_reference": {
        "tarif": "Code tarif officiel A, B, C ou D.",
        "periode": "Periode d'application du tarif.",
        "condition_retour": "Condition aller-retour avec client ou retour a vide.",
        "prix_km_eur": "Prix maximum par kilometre.",
        "prise_en_charge_eur": "Montant de prise en charge.",
        "course_minimum_eur": "Montant minimal d'une course.",
        "attente_marche_lente_eur_h": "Tarif horaire d'attente ou de marche lente.",
    },
}


@dataclass
class Profile:
    name: str
    fields: list[str] = field(default_factory=list)
    rows: int = 0
    empty_counts: Counter = field(default_factory=Counter)
    na_literal_counts: Counter = field(default_factory=Counter)
    examples: dict[str, list[str]] = field(default_factory=dict)
    distinct_small: dict[str, set[str]] = field(default_factory=dict)
    duplicate_exact_rows: int = 0
    duplicate_keys: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    min_max: dict[str, dict[str, Any]] = field(default_factory=dict)
    invalid_counts: Counter = field(default_factory=Counter)
    _exact_hashes: set[str] = field(default_factory=set, repr=False)
    _key_sets: dict[str, set[Any]] = field(default_factory=dict, repr=False)

    def init_fields(self, fields: list[str]) -> None:
        if not self.fields:
            self.fields = fields
            self.examples = {f: [] for f in fields}
            self.distinct_small = {f: set() for f in fields}

    def add_row(
        self,
        row: dict[str, Any],
        exact_duplicate: bool = False,
        key_specs: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        if not self.fields:
            self.init_fields(list(row.keys()))
        self.rows += 1
        values = [normalize_cell(row.get(field, "")) for field in self.fields]
        for field, value in zip(self.fields, values):
            stripped = value.strip()
            if stripped == "":
                self.empty_counts[field] += 1
            elif stripped.lower() in NA_LITERALS:
                self.na_literal_counts[field] += 1
            else:
                if len(self.examples[field]) < 3 and stripped not in self.examples[field]:
                    self.examples[field].append(stripped[:120])
                if len(self.distinct_small[field]) <= 20:
                    self.distinct_small[field].add(stripped[:120])

        if exact_duplicate:
            digest = hashlib.sha1("\u241f".join(values).encode("utf-8", "ignore")).hexdigest()
            if digest in self._exact_hashes:
                self.duplicate_exact_rows += 1
            else:
                self._exact_hashes.add(digest)

        if key_specs:
            for key_name, columns in key_specs.items():
                key = tuple(normalize_cell(row.get(col, "")).strip() for col in columns)
                if key_name not in self._key_sets:
                    self._key_sets[key_name] = set()
                if key in self._key_sets[key_name]:
                    self.duplicate_keys[key_name] = self.duplicate_keys.get(key_name, 0) + 1
                else:
                    self._key_sets[key_name].add(key)

    def set_min_max(self, field_name: str, value: Any) -> None:
        if value in (None, ""):
            return
        current = self.min_max.setdefault(field_name, {"min": value, "max": value})
        if value < current["min"]:
            current["min"] = value
        if value > current["max"]:
            current["max"] = value

    def to_jsonable(self) -> dict[str, Any]:
        columns = []
        for field_name in self.fields:
            empty = self.empty_counts.get(field_name, 0)
            na_literal = self.na_literal_counts.get(field_name, 0)
            missing = empty + na_literal
            completeness = None if self.rows == 0 else round((self.rows - missing) / self.rows * 100, 2)
            distinct_values = self.distinct_small.get(field_name, set())
            columns.append(
                {
                    "field": field_name,
                    "description": FIELD_DESCRIPTIONS.get(self.name, {}).get(field_name, ""),
                    "empty": empty,
                    "na_literal": na_literal,
                    "missing_total": missing,
                    "completeness_pct": completeness,
                    "examples": self.examples.get(field_name, []),
                    "distinct_sample": sorted(distinct_values)[:20],
                    "min_max": self.min_max.get(field_name),
                }
            )
        return {
            "name": self.name,
            "rows": self.rows,
            "columns": len(self.fields),
            "fields": self.fields,
            "duplicate_exact_rows": self.duplicate_exact_rows,
            "duplicate_keys": self.duplicate_keys,
            "invalid_counts": dict(self.invalid_counts),
            "notes": self.notes,
            "columns_profile": columns,
        }


def normalize_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def open_text_url(url: str, *, gz: bool = False) -> io.TextIOBase:
    req = urllib.request.Request(url, headers={"User-Agent": "mobilite-rhone-data-profiler/1.0"})
    response = urllib.request.urlopen(req, timeout=180)
    if gz:
        return io.TextIOWrapper(gzip.GzipFile(fileobj=response), encoding="utf-8", newline="")
    return io.TextIOWrapper(response, encoding="utf-8-sig", newline="")


def parse_date_any(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(value[:10] if fmt == "%Y-%m-%d" else value[:8], fmt).date()
        except ValueError:
            pass
    return None


def float_or_none(value: str) -> float | None:
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    if math.isnan(parsed):
        return None
    return parsed


def int_or_none(value: str) -> int | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(float(value.replace(",", ".")))
    except ValueError:
        return None


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def profile_csv_url(
    name: str,
    url: str,
    *,
    delimiter: str = ",",
    gz: bool = False,
    filter_fn=None,
    date_field: str | None = None,
    key_specs: dict[str, tuple[str, ...]] | None = None,
    exact_duplicate: bool = True,
) -> Profile:
    profile = Profile(name)
    with open_text_url(url, gz=gz) as text:
        reader = csv.DictReader(text, delimiter=delimiter)
        profile.init_fields(reader.fieldnames or [])
        for row in reader:
            if filter_fn and not filter_fn(row):
                continue
            profile.add_row(row, exact_duplicate=exact_duplicate, key_specs=key_specs)
            if date_field:
                parsed_date = parse_date_any(row.get(date_field, ""))
                if parsed_date:
                    profile.set_min_max(date_field, parsed_date.isoformat())
    return profile


def profile_rpc() -> tuple[Profile, dict[str, Any]]:
    profile = Profile("rpc_trajets_covoiturage_lyon")
    raw_counts = {}
    filtered_by_month = Counter()
    start_in_lyon = 0
    end_in_lyon = 0
    internal_lyon = 0
    out_path = DATA_DIR / "rpc_trajets_covoiturage_metropole_lyon_2026_01_03.csv"
    writer = None
    output_handle = None
    try:
        for month, url in RPC_MONTHS.items():
            print(f"[RPC] lecture {month}", flush=True)
            with open_text_url(url) as text:
                reader = csv.DictReader(text, delimiter=";")
                profile.init_fields(reader.fieldnames or [])
                if writer is None:
                    output_handle = out_path.open("w", encoding="utf-8", newline="")
                    writer = csv.DictWriter(output_handle, fieldnames=profile.fields, delimiter=";")
                    writer.writeheader()
                raw_count = 0
                for row in reader:
                    raw_count += 1
                    is_start_lyon = row.get("journey_start_towngroup") == LYON_TOWNGROUP
                    is_end_lyon = row.get("journey_end_towngroup") == LYON_TOWNGROUP
                    if not (is_start_lyon or is_end_lyon):
                        continue
                    filtered_by_month[month] += 1
                    start_in_lyon += int(is_start_lyon)
                    end_in_lyon += int(is_end_lyon)
                    internal_lyon += int(is_start_lyon and is_end_lyon)
                    profile.add_row(
                        row,
                        exact_duplicate=True,
                        key_specs={
                            "journey_id": ("journey_id",),
                            "journey_spatio_temporal_without_ids": (
                                "journey_start_datetime",
                                "journey_start_lon",
                                "journey_start_lat",
                                "journey_end_datetime",
                                "journey_end_lon",
                                "journey_end_lat",
                                "journey_distance",
                                "journey_duration",
                            ),
                        },
                    )
                    writer.writerow(row)
                    for date_field in ("journey_start_date", "journey_end_date"):
                        parsed_date = parse_date_any(row.get(date_field, ""))
                        if parsed_date:
                            profile.set_min_max(date_field, parsed_date.isoformat())
                    distance = int_or_none(row.get("journey_distance", ""))
                    duration = int_or_none(row.get("journey_duration", ""))
                    seats = int_or_none(row.get("passenger_seats", ""))
                    if distance is not None:
                        profile.set_min_max("journey_distance", distance)
                        if distance <= 0:
                            profile.invalid_counts["distance_non_positive"] += 1
                    if duration is not None:
                        profile.set_min_max("journey_duration", duration)
                        if duration <= 0:
                            profile.invalid_counts["duration_non_positive"] += 1
                    if seats is not None:
                        profile.set_min_max("passenger_seats", seats)
                        if seats <= 0:
                            profile.invalid_counts["passenger_seats_non_positive"] += 1
                    for lat_field, lon_field in (
                        ("journey_start_lat", "journey_start_lon"),
                        ("journey_end_lat", "journey_end_lon"),
                    ):
                        lat = float_or_none(row.get(lat_field, ""))
                        lon = float_or_none(row.get(lon_field, ""))
                        if lat is not None and not (-90 <= lat <= 90):
                            profile.invalid_counts[f"{lat_field}_out_of_range"] += 1
                        if lon is not None and not (-180 <= lon <= 180):
                            profile.invalid_counts[f"{lon_field}_out_of_range"] += 1
                raw_counts[month] = raw_count
    finally:
        if output_handle:
            output_handle.close()
    profile.notes.append(f"Filtre applique: depart ou arrivee dans '{LYON_TOWNGROUP}'.")
    profile.notes.append(f"Fichier filtre ecrit: {out_path.as_posix()}.")
    meta = {
        "raw_counts_by_month": raw_counts,
        "filtered_counts_by_month": dict(filtered_by_month),
        "start_in_lyon_rows": start_in_lyon,
        "end_in_lyon_rows": end_in_lyon,
        "internal_lyon_rows": internal_lyon,
        "output_csv": str(out_path),
    }
    return profile, meta


def profile_chantiers() -> tuple[Profile, dict[str, Any]]:
    rows_kept = []

    def overlaps_period(row: dict[str, str]) -> bool:
        start = parse_date_any(row.get("debutchantier", ""))
        end = parse_date_any(row.get("finchantier", ""))
        if start is None and end is None:
            return True
        start_ok = start is None or start < END_DATE_EXCLUSIVE
        end_ok = end is None or end >= START_DATE
        return start_ok and end_ok

    def collect_filter(row: dict[str, str]) -> bool:
        keep = overlaps_period(row)
        if keep:
            rows_kept.append(row)
        return keep

    profile = profile_csv_url(
        "chantiers_perturbants",
        URLS["chantiers_perturbants"],
        delimiter=",",
        filter_fn=collect_filter,
        date_field="debutchantier",
        key_specs={"gid": ("gid",), "FID": ("FID",)},
    )
    profile.notes.append("Filtre applique: chantier chevauchant janvier-mars 2026.")
    if rows_kept:
        write_csv(DATA_DIR / "chantiers_perturbants_jan_mar_2026.csv", rows_kept, profile.fields)
    meta = {"output_csv": str(DATA_DIR / "chantiers_perturbants_jan_mar_2026.csv")}
    return profile, meta


def profile_comptage_measures() -> tuple[Profile, dict[str, Any]]:
    profile = Profile("comptage_mesures_jan_mar_2026")
    profile.init_fields(["channel_id", "counter_id", "start_datetime", "end_datetime", "count"])
    page_size = 100000
    start = 1
    page = 0
    distinct_channels = set()
    distinct_counters = set()
    rows_by_month = Counter()
    while True:
        page += 1
        params = (
            f"?start_datetime__gte=2026-01-01"
            f"&start_datetime__lt=2026-04-01"
            f"&maxfeatures={page_size}"
            f"&start={start}"
        )
        url = COMPTAGE_MEASURES_URL + params
        print(f"[Comptage mesures] page {page}, start={start}", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "mobilite-rhone-data-profiler/1.0"})
        with urllib.request.urlopen(req, timeout=240) as response:
            payload = json.loads(response.read().decode("utf-8"))
        values = payload.get("values") or []
        for row in values:
            normalized = {field: normalize_cell(row.get(field, "")) for field in profile.fields}
            profile.add_row(
                normalized,
                exact_duplicate=True,
                key_specs={
                    "channel_start_end": ("channel_id", "start_datetime", "end_datetime"),
                },
            )
            distinct_channels.add(normalized.get("channel_id", ""))
            distinct_counters.add(normalized.get("counter_id", ""))
            start_dt = normalized.get("start_datetime", "")
            if len(start_dt) >= 7:
                rows_by_month[start_dt[:7]] += 1
            count_value = int_or_none(normalized.get("count", ""))
            if count_value is not None:
                profile.set_min_max("count", count_value)
                if count_value < 0:
                    profile.invalid_counts["count_negative"] += 1
            if start_dt:
                profile.set_min_max("start_datetime", start_dt)
            end_dt = normalized.get("end_datetime", "")
            if end_dt:
                profile.set_min_max("end_datetime", end_dt)
        if len(values) < page_size:
            break
        start += page_size
    profile.notes.append("Fenetre interrogee: start_datetime >= 2026-01-01 et < 2026-04-01.")
    meta = {
        "distinct_channels": len([value for value in distinct_channels if value]),
        "distinct_counters": len([value for value in distinct_counters if value]),
        "rows_by_month": dict(rows_by_month),
    }
    return profile, meta


def profile_meteo(name: str, url: str) -> tuple[Profile, dict[str, Any]]:
    rows_kept = []

    def in_period(row: dict[str, str]) -> bool:
        parsed = parse_date_any(row.get("AAAAMMJJ", ""))
        keep = parsed is not None and START_DATE <= parsed < END_DATE_EXCLUSIVE
        if keep:
            rows_kept.append(row)
        return keep

    profile = profile_csv_url(
        name,
        url,
        delimiter=";",
        gz=True,
        filter_fn=in_period,
        date_field="AAAAMMJJ",
        key_specs={"station_date": ("NUM_POSTE", "AAAAMMJJ")},
    )
    stations = Counter(row.get("NOM_USUEL", "") for row in rows_kept)
    profile.notes.append("Filtre applique: observations quotidiennes du departement 69 entre 2026-01-01 et 2026-03-31.")
    if rows_kept:
        write_csv(DATA_DIR / f"{name}.csv", rows_kept, profile.fields)
    return profile, {"stations": dict(stations), "output_csv": str(DATA_DIR / f"{name}.csv")}


def profile_tarifs() -> Profile:
    profile = Profile("tarifs_taxi_rhone_2026_reference")
    rows = [
        {
            "tarif": "A",
            "periode": "Jour 7h-19h",
            "condition_retour": "Aller et retour avec un client",
            "prix_km_eur": "1.00",
            "prise_en_charge_eur": "3.10",
            "course_minimum_eur": "8.00",
            "attente_marche_lente_eur_h": "41.30",
        },
        {
            "tarif": "B",
            "periode": "Nuit 19h-7h / dimanches / jours feries / routes enneigees",
            "condition_retour": "Aller et retour avec un client",
            "prix_km_eur": "1.50",
            "prise_en_charge_eur": "3.10",
            "course_minimum_eur": "8.00",
            "attente_marche_lente_eur_h": "41.30",
        },
        {
            "tarif": "C",
            "periode": "Jour 7h-19h",
            "condition_retour": "Aller avec un client et retour a vide",
            "prix_km_eur": "2.00",
            "prise_en_charge_eur": "3.10",
            "course_minimum_eur": "8.00",
            "attente_marche_lente_eur_h": "41.30",
        },
        {
            "tarif": "D",
            "periode": "Nuit 19h-7h / dimanches / jours feries / routes enneigees",
            "condition_retour": "Aller avec un client et retour a vide",
            "prix_km_eur": "3.00",
            "prise_en_charge_eur": "3.10",
            "course_minimum_eur": "8.00",
            "attente_marche_lente_eur_h": "41.30",
        },
    ]
    profile.init_fields(list(rows[0].keys()))
    for row in rows:
        profile.add_row(row, exact_duplicate=True, key_specs={"tarif": ("tarif",)})
    profile.notes.append("Reference saisie depuis la page tarifs maximum 2026 de la Metropole de Lyon.")
    write_csv(DATA_DIR / "tarifs_taxi_rhone_2026_reference.csv", rows, profile.fields)
    return profile


def enrich_numeric_minmax_for_static(profile: Profile, rows_path: Path | None = None) -> None:
    # Reserved for future refinements; static profiles already include completeness and examples.
    return


def download_meteo_descriptions() -> None:
    for key in ("meteo_desc_rr_t_vent", "meteo_desc_autres"):
        target = OUT_DIR / f"{key}.csv"
        with open_text_url(URLS[key]) as text:
            target.write_text(text.read(), encoding="utf-8")


def write_markdown(profiles: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    path = OUT_DIR / "dictionnaire_donnees_profiling.md"
    lines = []
    lines.append("# Dictionnaire de donnees et profiling - Mobilite Lyon")
    lines.append("")
    lines.append("Periode analysee : **1er janvier 2026 au 31 mars 2026**.")
    lines.append("")
    lines.append("Les statistiques ci-dessous sont calculees sur les donnees retenues pour le projet, c'est-a-dire filtrees sur le perimetre utile quand un filtre est indique.")
    lines.append("")
    lines.append("## Synthese des tables")
    lines.append("")
    lines.append("| Table | Lignes | Colonnes | Doublons exacts | Doublons de cle | Commentaire |")
    lines.append("|---|---:|---:|---:|---|---|")
    for profile in profiles:
        duplicate_keys = ", ".join(f"{k}: {v}" for k, v in profile.get("duplicate_keys", {}).items()) or "0"
        notes = " ".join(profile.get("notes", []))[:180]
        lines.append(
            f"| `{profile['name']}` | {profile['rows']} | {profile['columns']} | "
            f"{profile['duplicate_exact_rows']} | {duplicate_keys} | {notes} |"
        )
    lines.append("")
    lines.append("## Cles relationnelles proposees")
    lines.append("")
    lines.append("| Source | Cle primaire / naturelle | Peut rejoindre | Cle de jointure | Usage |")
    lines.append("|---|---|---|---|---|")
    relation_rows = [
        ("rpc_trajets_covoiturage_lyon", "journey_id", "stations_taxi", "journey_start_insee / journey_end_insee -> insee", "Analyse par commune et proximite geographique."),
        ("rpc_trajets_covoiturage_lyon", "journey_id", "meteo_rr_t_vent_jan_mar_2026", "journey_start_date -> AAAAMMJJ", "Enrichissement meteo journalier."),
        ("rpc_trajets_covoiturage_lyon", "journey_id", "chantiers_perturbants", "journey_start_date entre debutchantier et finchantier + zone/commune", "Contexte perturbations travaux."),
        ("comptage_mesures_jan_mar_2026", "channel_id + start_datetime + end_datetime", "comptage_channels", "channel_id", "Description du canal mesure."),
        ("comptage_channels", "channel_id", "comptage_sites", "site_id", "Localisation du site de comptage."),
        ("rpc_trajets_covoiturage_lyon", "journey_id", "tarifs_taxi_rhone_2026_reference", "heure/jour -> tarif A/B/C/D", "Simulation de revenu taxi."),
    ]
    for row in relation_rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    for profile in profiles:
        lines.append(f"## `{profile['name']}`")
        lines.append("")
        lines.append(f"- Lignes : **{profile['rows']}**")
        lines.append(f"- Colonnes : **{profile['columns']}**")
        lines.append(f"- Doublons exacts : **{profile['duplicate_exact_rows']}**")
        if profile.get("duplicate_keys"):
            lines.append("- Doublons de cle : " + ", ".join(f"`{k}` = {v}" for k, v in profile["duplicate_keys"].items()))
        if profile.get("invalid_counts"):
            lines.append("- Valeurs invalides detectees : " + ", ".join(f"`{k}` = {v}" for k, v in profile["invalid_counts"].items()))
        if profile.get("notes"):
            for note in profile["notes"]:
                lines.append(f"- Note : {note}")
        lines.append("")
        lines.append("| Champ | Description | Vides | NA litteraux | Completude | Exemples |")
        lines.append("|---|---|---:|---:|---:|---|")
        for col in profile["columns_profile"]:
            examples = ", ".join(f"`{x}`" for x in col.get("examples", [])[:2])
            completeness = "" if col["completeness_pct"] is None else f"{col['completeness_pct']}%"
            desc = col.get("description", "")
            lines.append(
                f"| `{col['field']}` | {desc} | {col['empty']} | {col['na_literal']} | {completeness} | {examples} |"
            )
        lines.append("")
    lines.append("## Metadonnees complementaires")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(meta, ensure_ascii=False, indent=2, default=str))
    lines.append("```")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    started = time.time()
    profiles = []
    meta: dict[str, Any] = {}

    rpc_profile, rpc_meta = profile_rpc()
    profiles.append(rpc_profile.to_jsonable())
    meta["rpc"] = rpc_meta

    print("[Stations taxi] lecture", flush=True)
    stations_profile = profile_csv_url(
        "stations_taxi",
        URLS["stations_taxi"],
        delimiter=",",
        key_specs={"gid": ("gid",), "FID": ("FID",)},
    )
    profiles.append(stations_profile.to_jsonable())

    print("[Chantiers] lecture", flush=True)
    chantiers_profile, chantiers_meta = profile_chantiers()
    profiles.append(chantiers_profile.to_jsonable())
    meta["chantiers"] = chantiers_meta

    print("[Comptage sites] lecture", flush=True)
    comptage_sites_profile = profile_csv_url(
        "comptage_sites",
        URLS["comptage_sites"],
        delimiter=",",
        key_specs={"site_id": ("site_id",), "FID": ("FID",)},
    )
    profiles.append(comptage_sites_profile.to_jsonable())

    print("[Comptage channels] lecture", flush=True)
    comptage_channels_profile = profile_csv_url(
        "comptage_channels",
        URLS["comptage_channels"],
        delimiter=";",
        key_specs={"channel_id": ("channel_id",)},
    )
    profiles.append(comptage_channels_profile.to_jsonable())

    comptage_measures_profile, comptage_meta = profile_comptage_measures()
    profiles.append(comptage_measures_profile.to_jsonable())
    meta["comptage_mesures"] = comptage_meta

    print("[Meteo RR-T-Vent] lecture", flush=True)
    meteo_rr_profile, meteo_rr_meta = profile_meteo("meteo_rr_t_vent_jan_mar_2026", URLS["meteo_rr_t_vent"])
    profiles.append(meteo_rr_profile.to_jsonable())
    meta["meteo_rr_t_vent"] = meteo_rr_meta

    print("[Meteo autres] lecture", flush=True)
    meteo_autres_profile, meteo_autres_meta = profile_meteo("meteo_autres_jan_mar_2026", URLS["meteo_autres"])
    profiles.append(meteo_autres_profile.to_jsonable())
    meta["meteo_autres"] = meteo_autres_meta

    print("[Meteo descriptions] lecture", flush=True)
    download_meteo_descriptions()

    tarifs_profile = profile_tarifs()
    profiles.append(tarifs_profile.to_jsonable())

    meta["runtime_seconds"] = round(time.time() - started, 2)
    meta["generated_at"] = datetime.now().isoformat(timespec="seconds")

    (OUT_DIR / "profiling_resultats.json").write_text(
        json.dumps({"profiles": profiles, "meta": meta}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    write_markdown(profiles, meta)
    print(f"[OK] Profiling termine en {meta['runtime_seconds']} secondes", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
