import requests
from bs4 import BeautifulSoup, Tag
from typing import Optional, Dict, List
import json
import re  # Dodaj import modułu re dla wyrażeń regularnych
from datetime import datetime
from urllib.parse import quote

BASE_URL = "https://www.dekudeals.com"


def parse_release_dates(raw_text: str) -> Dict[str, str]:
    """
    Parsuje surowy tekst dat wydania na strukturę platform -> data.

    Input przykład: ":PS4, SwitchJanuary 25, 2018Xbox OneJanuary 26, 2018"
    Output: {"PS4": "January 25, 2018", "Switch": "January 25, 2018", "Xbox One": "January 26, 2018"}
    """
    if not raw_text or raw_text.strip() == ":":
        return {"unknown": "Unknown release date"}

    # Usuń dwukropek z początku
    clean_text = raw_text.lstrip(":").strip()

    # Znane platformy
    platforms = [
        "PlayStation 5",
        "PS5",
        "PlayStation 4",
        "PS4",
        "Xbox Series X/S",
        "Xbox Series",
        "Xbox One",
        "Switch",
        "Nintendo Switch",
        "PC",
        "Steam",
    ]

    # Regex dla dat w formacie "Month Day, Year"
    date_pattern = r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})"

    # Znajdź wszystkie daty
    dates = re.findall(date_pattern, clean_text)

    if not dates:
        return {"all_platforms": clean_text}

    result = {}
    current_text = clean_text

    # Dla każdej znalezionej daty, znajdź platformy przed nią
    for date in dates:
        # Znajdź pozycję daty w tekście
        date_pos = current_text.find(date)
        if date_pos == -1:
            continue

        # Tekst przed datą zawiera platformy
        before_date = current_text[:date_pos]

        # Znajdź platformy w tekście przed datą
        found_platforms = []
        for platform in platforms:
            if platform in before_date:
                found_platforms.append(platform)
                # Usuń znalezioną platformę z tekstu, żeby nie duplikować
                before_date = before_date.replace(platform, "", 1)

        # Jeśli znaleziono platformy, przypisz im datę
        if found_platforms:
            for platform in found_platforms:
                result[platform] = date
        else:
            # Jeśli nie znaleziono konkretnych platform, użyj generycznego klucza
            if "unknown_platforms" not in result:
                result["unknown_platforms"] = []
            result["unknown_platforms"].append(date)

        # Usuń przetworzoną część z tekstu
        current_text = current_text[date_pos + len(date) :]

    return result if result else {"all_platforms": clean_text}


def search_deku_deals(query: str) -> Optional[str]:
    """
    Wyszukuje grę na DekuDeals.com i zwraca URL do jej strony produktu.
    Zwraca None, jeśli gra nie została znaleziona w pierwszych wynikach.
    """
    search_url = f"{BASE_URL}/search?q={quote(query)}"
    print(f"Szukam gry '{query}' na: {search_url}")

    try:
        response = requests.get(search_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Poprawiony selektor na podstawie Twojego odkrycia
        first_result_link = soup.find("a", class_="main-link")

        if (
            first_result_link
            and isinstance(first_result_link, Tag)
            and first_result_link.get("href")
        ):
            game_path = first_result_link.get("href")
            full_game_url = f"{BASE_URL}{game_path}"
            print(f"Znaleziono potencjalny URL dla '{query}': {full_game_url}")
            return full_game_url
        else:
            print(f"Nie znaleziono bezpośredniego linku do gry dla '{query}'.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Błąd sieciowy podczas wyszukiwania gry '{query}': {e}")
        return None
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas parsowania wyników wyszukiwania: {e}")
        return None


def scrape_game_details(game_url: str) -> Optional[Dict]:
    """
    Scrapuje szczegółowe dane o grze z jej strony DekuDeals.
    Zwraca słownik z danymi lub None w przypadku błędu/braku danych.
    """
    print(f"Scrapuję szczegóły z URL: {game_url}")

    try:
        response = requests.get(game_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        game_details = {}

        # --- Tytuł Gry ---
        # Widać, że tytuł jest w <span class='display-5 item-title'> wewnątrz <h2>
        title_tag = soup.find("span", class_="item-title")
        if title_tag:
            game_details["title"] = title_tag.get_text(strip=True)
        else:
            game_details["title"] = "Nieznany tytuł"

        # --- Sekcja 'Details' (list-group) ---
        details_list = soup.find("ul", class_="details")
        if details_list:
            # Iteruj przez wszystkie elementy listy w sekcji 'Details'
            for li in details_list.find_all("li", class_="list-group-item"):
                strong_tag = li.find("strong")
                if not strong_tag:
                    continue  # Pomijamy elementy bez strong (np. te zagnieżdżone ul dla player modes)

                label = strong_tag.get_text(strip=True).replace(":", "")  # Np. 'MSRP'

                # Użyj find_next_sibling('dd') dla pewności, lub po prostu .find() dla a
                # Sprawdź, co następuje po strong i jak wyciągnąć tekst

                # --- MSRP ---
                if "MSRP" in label:
                    # Cena jest bezpośrednio po strong, lub w innerHTML
                    msrp_text = li.get_text(strip=True).replace(label, "").strip()
                    game_details["MSRP"] = msrp_text

                # --- Release date ---
                elif "Release date" in label:
                    release_date_text = (
                        li.get_text(strip=True).replace(label, "").strip()
                    )
                    # Parsuj surowy tekst na strukturę użyteczną dla AI
                    parsed_release_dates = parse_release_dates(release_date_text)
                    game_details["release_date"] = (
                        release_date_text  # Zachowaj surowy dla debug
                    )
                    game_details["release_dates_parsed"] = (
                        parsed_release_dates  # Dodaj sparsowane dane
                    )

                # --- Genre ---
                elif "Genre" in label:
                    genres = [
                        a.get_text(strip=True)
                        for a in li.find_all(
                            "a", href=re.compile(r"/games\?filter\[genre\]=")
                        )
                    ]
                    game_details["genres"] = genres if genres else ["Nieznany"]

                # --- Developer ---
                elif "Developer" in label:
                    dev_tag = li.find(
                        "a", href=re.compile(r"/games\?filter\[developer\]=")
                    )
                    if dev_tag:
                        game_details["developer"] = dev_tag.get_text(strip=True)
                    else:
                        game_details["developer"] = "Nieznany"

                # --- Publisher ---
                elif "Publisher" in label:
                    pub_tag = li.find(
                        "a", href=re.compile(r"/games\?filter\[publisher\]=")
                    )
                    if pub_tag:
                        game_details["publisher"] = pub_tag.get_text(strip=True)
                    else:
                        game_details["publisher"] = "Nieznany"

                # --- Metacritic ---
                elif "Metacritic" in label:
                    metacritic_link = li.find("a", class_="metacritic")
                    if metacritic_link:
                        # Pierwszy span to wynik Metacritic, drugi to User Score (opcjonalnie)
                        scores = metacritic_link.find_all("span")
                        if scores:
                            game_details["metacritic_score"] = scores[0].get_text(
                                strip=True
                            )
                        if len(scores) > 1:
                            game_details["metacritic_user_score"] = scores[1].get_text(
                                strip=True
                            )
                    else:
                        game_details["metacritic_score"] = "Brak oceny"
                        game_details["metacritic_user_score"] = "Brak oceny"

                # --- OpenCritic ---
                elif "OpenCritic" in label:
                    opencritic_link = li.find("a", class_="opencritic")
                    if opencritic_link:
                        # Wynik jest bezpośrednio po div'ie z klasą 'opencritic-tier'
                        # Lub jest ostatnim tekstem w linku a
                        score_text = "".join(
                            opencritic_link.find_all(string=True, recursive=False)
                        ).strip()
                        game_details["opencritic_score"] = score_text
                    else:
                        game_details["opencritic_score"] = "Brak oceny"

                # --- Platformy ---
                # Jak zauważyłeś, "Platforms" to ostatni element <li> w 'details' list
                # Sprawdź, czy `li` zawiera tekst "Platforms", a następnie pobierz jego tekst
                if "Platforms" in label:  # `Platforms:`
                    # Tekst platformy jest bezpośrednio w li, po strong
                    platform_text = li.get_text(strip=True).replace(label, "").strip()
                    game_details["platform"] = platform_text

        else:
            print("Nie znaleziono sekcji 'Details'.")

        # --- Aktualne Ceny (z tabeli) ---
        # Zidentyfikowana tabela: <table class='table table-align-middle item-price-table'>
        price_table = soup.find("table", class_="item-price-table")
        if price_table:
            # Pierwszy wiersz (tr) z ceną jest zazwyczaj aktualną ceną eShop (digital)
            first_price_row = price_table.find("tr")
            if first_price_row:
                price_button_tag = first_price_row.find(
                    "div", class_="btn-primary"
                )  # Przycisk z ceną
                if price_button_tag:
                    game_details["current_eshop_price"] = price_button_tag.get_text(
                        strip=True
                    )
                else:
                    game_details["current_eshop_price"] = "N/A"
            else:
                game_details["current_eshop_price"] = "N/A"
        else:
            print("Nie znaleziono tabeli cen.")
            game_details["current_eshop_price"] = "N/A"

        # --- Najniższa Cena w Historii ---
        # Znajduje się w sekcji 'Price history'
        price_history_section = soup.find("div", id="price-history")
        if price_history_section:
            # Szukaj tekstu 'All time low' i obok niego ceny
            all_time_low_row = price_history_section.find(
                "strong", string="All time low"
            )
            if all_time_low_row:
                # Cena jest w następnym <td> po <tr> zawierającym 'All time low'
                # lub w td z klasą 'text-right pl-3'
                lowest_price_td = (
                    all_time_low_row.find_parent("tr")
                    .find_next_sibling("tr")
                    .find("td", class_="text-right")
                )
                if lowest_price_td:
                    game_details["lowest_historical_price"] = lowest_price_td.get_text(
                        strip=True
                    )
                else:
                    game_details["lowest_historical_price"] = (
                        "Brak danych o najniższej cenie"
                    )
            else:
                game_details["lowest_historical_price"] = (
                    "Brak danych o najniższej cenie"
                )
        else:
            print("Nie znaleziono sekcji 'Price history'.")
            game_details["lowest_historical_price"] = "Brak danych o historii cen"

        print(f"Szczegóły zebrane dla {game_details.get('title', 'gry')}:")

        return game_details

    except requests.exceptions.RequestException as e:
        print(f"Błąd sieciowy podczas scrapowania szczegółów z '{game_url}': {e}")
        return None
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas parsowania szczegółów z '{game_url}': {e}")
        return None


def scrape_dekudeals_collection(collection_url: str) -> Dict[str, any]:
    """
    Scrapuje kolekcję gier z DekuDeals i zwraca listę nazw gier.

    Args:
        collection_url (str): URL do kolekcji DekuDeals (np. https://www.dekudeals.com/collection/xxx)

    Returns:
        Dict zawierający:
        - success (bool): Czy operacja się powiodła
        - games (List[str]): Lista nazw gier
        - game_count (int): Liczba znalezionych gier
        - error (str): Błąd jeśli wystąpił
    """
    try:
        print(f"Parsuje kolekcję DekuDeals: {collection_url}")

        # Walidacja URL
        if not collection_url or "dekudeals.com/collection/" not in collection_url:
            return {
                "success": False,
                "error": "Nieprawidłowy URL kolekcji DekuDeals",
                "games": [],
                "game_count": 0,
            }

        # Pobierz stronę kolekcji
        response = requests.get(collection_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Lista do przechowywania nazw gier
        game_titles = []

        # Znajdź wszystkie gry w kolekcji
        # Na podstawie struktury strony, szukamy elementów które zawierają nazwy gier
        # Możliwe selektory dla gier w kolekcji
        game_selectors = [
            "h3",  # Główne nagłówki gier
            ".game-title",  # Ewentualne klasy z tytułami
            "[data-game-title]",  # Elementy z atrybutami tytułów
            "a[href*='/items/']",  # Linki do stron gier
        ]

        # Próbujemy różne selektory
        for selector in game_selectors:
            elements = soup.select(selector)
            if elements:
                print(
                    f"Znaleziono {len(elements)} elementów używając selektora: {selector}"
                )

                for element in elements:
                    if isinstance(element, Tag):
                        # Wyciągnij tekst z elementu
                        title_text = element.get_text(strip=True)

                        # Sprawdź czy to wygląda jak tytuł gry (nie jest pusty, nie zawiera tylko cyfr)
                        if (
                            title_text
                            and len(title_text) > 2
                            and not title_text.isdigit()
                        ):
                            # Czyść tytuł z niepotrzebnych elementów
                            cleaned_title = clean_game_title(title_text)
                            if cleaned_title and cleaned_title not in game_titles:
                                game_titles.append(cleaned_title)

                # Jeśli znaleźliśmy gry, przerywamy pętlę
                if game_titles:
                    break

        # Jeśli nie znaleźliśmy gier standardowymi metodami, spróbuj alternatywnych
        if not game_titles:
            print("Próbuję alternatywnych metod parsowania...")

            # Szukaj w całym tekście strony tytułów gier
            # Możemy szukać wzorców tekstowych charakterystycznych dla gier
            all_text = soup.get_text()

            # Podziel tekst na linie i szukaj potencjalnych tytułów gier
            lines = all_text.split("\n")
            for line in lines:
                line = line.strip()
                # Sprawdź czy linia wygląda jak tytuł gry
                if (
                    line
                    and len(line) > 3
                    and len(line) < 100
                    and not line.isdigit()
                    and not line.startswith("$")
                    and not line.lower().startswith("rating")
                    and not line.lower().startswith("format")
                    and not line.lower().startswith("platform")
                ):

                    # Dodatkowe filtrowanie dla typowych tytułów gier
                    if any(
                        keyword in line.lower()
                        for keyword in [
                            "edition",
                            "collection",
                            "ultimate",
                            "deluxe",
                            "remastered",
                            ":",
                        ]
                    ):
                        cleaned_title = clean_game_title(line)
                        if cleaned_title and cleaned_title not in game_titles:
                            game_titles.append(cleaned_title)

        # Usuń duplikaty zachowując kolejność
        unique_titles = []
        seen = set()
        for title in game_titles:
            if title not in seen:
                unique_titles.append(title)
                seen.add(title)

        print(f"Znaleziono {len(unique_titles)} unikalnych gier w kolekcji")

        return {
            "success": True,
            "games": unique_titles,
            "game_count": len(unique_titles),
            "collection_url": collection_url,
        }

    except requests.exceptions.RequestException as e:
        error_msg = f"Błąd sieciowy podczas pobierania kolekcji: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg, "games": [], "game_count": 0}
    except Exception as e:
        error_msg = f"Błąd podczas parsowania kolekcji: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg, "games": [], "game_count": 0}


def clean_game_title(title: str) -> str:
    """
    Czyści tytuł gry z niepotrzebnych elementów.

    Args:
        title (str): Surowy tytuł gry

    Returns:
        str: Oczyszczony tytuł gry
    """
    if not title:
        return ""

    # Usuń białe znaki z początku i końca
    cleaned = title.strip()

    # Usuń typowe słowa/frazy które nie są częścią tytułu
    unwanted_patterns = [
        r"\s*Rating\s*",
        r"\s*Format\s*",
        r"\s*Platform\s*",
        r"\s*Digital\s*",
        r"\s*Switch\s*$",
        r"\s*Add to\s*",
        r"\s*Hide\s*",
        r"^\s*🔔\s*",
        r"\s*\d+\s*items?\s*$",
    ]

    for pattern in unwanted_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Usuń nadmiarowe białe znaki
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Sprawdź czy po czyszczeniu coś zostało
    if len(cleaned) < 2:
        return ""

    return cleaned


# --- Zaktualizowany blok testowy w __main__ ---
if __name__ == "__main__":
    print("Testowanie funkcji search_deku_deals i scrape_game_details...")

    # Test nowej funkcji parsowania kolekcji
    print("\n=== TESTOWANIE PARSOWANIA KOLEKCJI DEKUDEALS ===")
    collection_url = "https://www.dekudeals.com/collection/nbb76ddx3t"
    print(f"Testuję parsowanie kolekcji: {collection_url}")

    collection_result = scrape_dekudeals_collection(collection_url)
    if collection_result["success"]:
        print(f"✅ Sukces! Znaleziono {collection_result['game_count']} gier:")
        for i, game in enumerate(collection_result["games"][:10], 1):
            print(f"  {i:2d}. {game}")
        if collection_result["game_count"] > 10:
            print(f"     ... i {collection_result['game_count'] - 10} więcej gier")
    else:
        print(f"❌ Błąd: {collection_result['error']}")

    print("\n=== TESTOWANIE WYSZUKIWANIA POJEDYNCZYCH GIER ===")
    test_games = [
        "The Legend of Zelda: Tears of the Kingdom",
        "Hollow Knight",
        "Cuphead",
        "Celeste",  # Dodaj inną grę, żeby sprawdzić, czy działa dla różnych
        "Super Mario Odyssey",
        "Witcher 3",
        "baba is you",
        "Transistor",
        "streets of rogue",
        "the last of us",
    ]

    for game_name in test_games:
        print(f"\n--- Przetwarzam grę: {game_name} ---")
        game_url = search_deku_deals(game_name)
        if game_url:
            game_details = scrape_game_details(game_url)
            if game_details:
                print(f"Pomyślnie zesrapowano dane dla {game_name}.")
            else:
                print(f"Nie udało się zesrapować szczegółów dla {game_name}.")
        else:
            print(f"Nie znaleziono URL dla {game_name}.")
        print("-" * 30)
