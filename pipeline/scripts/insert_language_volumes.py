"""One-shot: insert DataForSEO volume data into language_opportunity table."""
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from pipeline.core.stage0_language import run_migration, LANGUAGES, CONCEPTS, LANG_DISPLAY

DB = Path(__file__).resolve().parent.parent / "data" / "registry.db"

# Volume data from DataForSEO kw_data_google_ads_search_volume calls
# Key: '{lang_display} {concept_normalised}'  Value: monthly search volume
# 0 = keyword appeared in results but had no search_volume (no measurable demand)
RAW: dict[str, int] = {
    # Python
    "python async await": 390, "python class inheritance": 1000, "python closure": 590,
    "python context manager": 1900, "python dataclass": 5400, "python decorator pattern": 90,
    "python dictionary comprehension": 2900, "python environment variables": 1000,
    "python error handling": 0, "python file handling": 210, "python generator function": 390,
    "python http requests": 590, "python json parsing": 1600, "python lambda function": 2400,
    "python list comprehension": 4400, "python recursion": 1000, "python regex pattern": 110,
    "python sorting algorithm": 480, "python string formatting": 6600, "python type hints": 2400,
    # JavaScript
    "javascript async await": 1900, "javascript class inheritance": 110,
    "javascript closure": 1600, "javascript context manager": 10,
    "javascript dataclass": 10, "javascript decorator pattern": 10,
    "javascript dictionary comprehension": 0, "javascript environment variables": 70,
    "javascript error handling": 0, "javascript file handling": 10,
    "javascript generator function": 210, "javascript http requests": 210,
    "javascript json parsing": 720, "javascript lambda function": 140,
    "javascript list comprehension": 170, "javascript recursion": 170,
    "javascript regex pattern": 20, "javascript sorting algorithm": 30,
    "javascript string formatting": 1300, "javascript type hints": 70,
    # TypeScript
    "typescript async await": 170, "typescript class inheritance": 50,
    "typescript closure": 30, "typescript context manager": 0,
    "typescript dataclass": 20, "typescript decorator pattern": 10,
    "typescript dictionary comprehension": 0, "typescript environment variables": 40,
    "typescript error handling": 0, "typescript file handling": 0,
    "typescript generator function": 30, "typescript http requests": 0,
    "typescript json parsing": 70, "typescript lambda function": 50,
    "typescript list comprehension": 30, "typescript recursion": 10,
    "typescript regex pattern": 10, "typescript sorting algorithm": 0,
    "typescript string formatting": 260, "typescript type hints": 10,
    # Go
    "go async await": 30, "go class inheritance": 0, "go closure": 90,
    "go context manager": 0, "go dataclass": 0, "go decorator pattern": 10,
    "go dictionary comprehension": 0, "go environment variables": 210,
    "go error handling": 0, "go file handling": 10, "go generator function": 0,
    "go http requests": 260, "go json parsing": 70, "go lambda function": 70,
    "go list comprehension": 10, "go recursion": 10, "go regex pattern": 0,
    "go sorting algorithm": 0, "go string formatting": 210, "go type hints": 0,
    # Rust
    "rust async await": 70, "rust class inheritance": 10, "rust closure": 320,
    "rust context manager": 10, "rust dataclass": 0, "rust decorator pattern": 10,
    "rust dictionary comprehension": 0, "rust environment variables": 110,
    "rust error handling": 0, "rust file handling": 10, "rust generator function": 10,
    "rust http requests": 70, "rust json parsing": 10, "rust lambda function": 50,
    "rust list comprehension": 20, "rust recursion": 30, "rust regex pattern": 0,
    "rust sorting algorithm": 10, "rust string formatting": 140, "rust type hints": 0,
    # Java
    "java async await": 110, "java class inheritance": 140, "java closure": 90,
    "java context manager": 10, "java dataclass": 140, "java decorator pattern": 390,
    "java dictionary comprehension": 0, "java environment variables": 260,
    "java error handling": 0, "java file handling": 30, "java generator function": 10,
    "java http requests": 170, "java json parsing": 590, "java lambda function": 2900,
    "java list comprehension": 50, "java recursion": 1300, "java regex pattern": 210,
    "java sorting algorithm": 480, "java string formatting": 2900, "java type hints": 0,
    # C#
    "c# async await": 480, "c# class inheritance": 140, "c# closure": 50,
    "c# context manager": 10, "c# dataclass": 30, "c# decorator pattern": 210,
    "c# dictionary comprehension": 0, "c# environment variables": 70,
    "c# error handling": 0, "c# file handling": 20, "c# generator function": 10,
    "c# http requests": 110, "c# json parsing": 260, "c# lambda function": 1000,
    "c# list comprehension": 50, "c# recursion": 70, "c# regex pattern": 20,
    "c# sorting algorithm": 70, "c# string formatting": 1600, "c# type hints": 0,
    # PHP
    "php async await": 10, "php class inheritance": 20, "php closure": 70,
    "php context manager": 0, "php dataclass": 10, "php decorator pattern": 30,
    "php dictionary comprehension": 0, "php environment variables": 210,
    "php error handling": 0, "php file handling": 10, "php generator function": 10,
    "php http requests": 30, "php json parsing": 110, "php lambda function": 140,
    "php list comprehension": 10, "php recursion": 20, "php regex pattern": 10,
    "php sorting algorithm": 0, "php string formatting": 30, "php type hints": 70,
    # Ruby
    "ruby async await": 10, "ruby class inheritance": 20, "ruby closure": 20,
    "ruby context manager": 0, "ruby dataclass": 0, "ruby decorator pattern": 30,
    "ruby dictionary comprehension": 0, "ruby environment variables": 30,
    "ruby error handling": 0, "ruby file handling": 10, "ruby generator function": 10,
    "ruby http requests": 0, "ruby json parsing": 170, "ruby lambda function": 210,
    "ruby list comprehension": 10, "ruby recursion": 10, "ruby regex pattern": 0,
    "ruby sorting algorithm": 10, "ruby string formatting": 70, "ruby type hints": 20,
    # Swift
    "swift async await": 90, "swift class inheritance": 10, "swift closure": 320,
    "swift context manager": 0, "swift dataclass": 0, "swift decorator pattern": 10,
    "swift dictionary comprehension": 0, "swift environment variables": 20,
    "swift error handling": 0, "swift file handling": 0, "swift generator function": 0,
    "swift http requests": 0, "swift json parsing": 40, "swift lambda function": 10,
    "swift list comprehension": 10, "swift recursion": 10, "swift regex pattern": 0,
    "swift sorting algorithm": 0, "swift string formatting": 0, "swift type hints": 0,
    # Kotlin
    "kotlin async await": 40, "kotlin class inheritance": 20, "kotlin closure": 20,
    "kotlin context manager": 0, "kotlin dataclass": 480, "kotlin decorator pattern": 10,
    "kotlin dictionary comprehension": 0, "kotlin environment variables": 10,
    "kotlin error handling": 0, "kotlin file handling": 10, "kotlin generator function": 10,
    "kotlin http requests": 20, "kotlin json parsing": 20, "kotlin lambda function": 50,
    "kotlin list comprehension": 10, "kotlin recursion": 10, "kotlin regex pattern": 10,
    "kotlin sorting algorithm": 0, "kotlin string formatting": 90, "kotlin type hints": 0,
    # C++
    "c++ async await": 70, "c++ class inheritance": 260, "c++ closure": 70,
    "c++ context manager": 10, "c++ dataclass": 10, "c++ decorator pattern": 70,
    "c++ dictionary comprehension": 0, "c++ environment variables": 20,
    "c++ error handling": 0, "c++ file handling": 90, "c++ generator function": 10,
    "c++ http requests": 40, "c++ json parsing": 210, "c++ lambda function": 3600,
    "c++ list comprehension": 20, "c++ recursion": 320, "c++ regex pattern": 10,
    "c++ sorting algorithm": 210, "c++ string formatting": 590, "c++ type hints": 0,
}


def canonical_kw(lang: str, concept: str) -> str:
    display = LANG_DISPLAY[lang]
    c = concept.replace(" example", "")
    return f"{display} {c}"


def main() -> None:
    run_migration(DB)
    conn = sqlite3.connect(str(DB))
    inserted = 0

    for lang in LANGUAGES:
        for concept in CONCEPTS:
            kw = canonical_kw(lang, concept)
            vol = RAW.get(kw, 0) or 0
            has_demand = 1 if vol > 0 else 0
            opp = float(vol)
            conn.execute(
                """INSERT INTO language_opportunity
                       (language, concept, canonical_keyword, volume, kd,
                        opportunity_score, has_demand, fetched_at)
                   VALUES (?,?,?,?,0,?,?,datetime('now'))
                   ON CONFLICT(language, concept) DO UPDATE SET
                       canonical_keyword = excluded.canonical_keyword,
                       volume            = excluded.volume,
                       opportunity_score = excluded.opportunity_score,
                       has_demand        = excluded.has_demand,
                       fetched_at        = excluded.fetched_at""",
                (lang, concept, kw, vol, opp, has_demand),
            )
            inserted += 1

    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM language_opportunity").fetchone()[0]
    with_demand = conn.execute(
        "SELECT COUNT(*) FROM language_opportunity WHERE has_demand=1"
    ).fetchone()[0]
    top5 = conn.execute(
        """SELECT language, concept, canonical_keyword, volume, opportunity_score
           FROM language_opportunity WHERE has_demand=1
           ORDER BY opportunity_score DESC LIMIT 5"""
    ).fetchall()
    conn.close()

    print(f"Upserted {inserted} cells into language_opportunity")
    print(f"Total rows: {total} | With demand: {with_demand} | Zero-demand: {total - with_demand}")
    print("\nTop 5 by opportunity score:")
    for i, r in enumerate(top5, 1):
        print(f"  {i}. {r[0]} / {r[1]} — \"{r[2]}\"  vol={r[3]}  opp={r[4]:.0f}")


if __name__ == "__main__":
    main()
