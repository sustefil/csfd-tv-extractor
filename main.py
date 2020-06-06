import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class Movie:



class CSFD:
    RATING_THRESHOLD = 80
    URL_TV = 'https://www.csfd.cz/televize/'
    URL_BASE = 'https://www.csfd.cz'

    def __init__(self):
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}

    def _generate_tv_stations_cookie():
        """
        As observed from diggin in the CSFD page, the channels you choose to view are stored in the cookies,
        so in order to fetch all the channels, just pre-generate all of them
        :return: str: cookie containing all the channels
        """
        result = '2%'
        for i in range(200):
            result += f'2C{i}%'

        return result

    def _get_main_tv_page(self, day=0):
        # To get all the tv programs, cookie has to be set
        cookies = {'tv_stations': self._generate_tv_stations_cookie()}

        r = self.session.get(f'https://www.csfd.cz/televize/?day={day}',
                             headers=self.headers, cookies=cookies)

        return r.text

    def get_film_page(self, film: str):
        r = self.session.get(self.URL_BASE + film, headers=self.headers)
        return r

    def gather_all_films_from_tv_program(self, daysback=0):
        all_films = []

        # X days back and today included
        for day in range(-daysback, 1):
            tv_page = self._get_main_tv_page(day)
            tv_page_soup = BeautifulSoup(tv_page, 'html.parser')

            film_links = tv_page_soup.find_all('a', class_='film c1')

            all_films.extend(film_links)

        return all_films


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    csfd = CSFD()

    print('Diggin CSFD TV, this may take a while..')
    all_films = csfd.gather_all_films_from_tv_program(daysback=0)

    extracted_films = []

    print('Going through the films to get the rating, this may take a while as well..')
    for film in all_films[:1000]:
        r = csfd.get_film_page(film.get('href'))

        soup_film = BeautifulSoup(r.text, 'html.parser')

        rating = soup_film.find('h2', class_='average')

        try:
            rating = int(rating.text.strip('%'))
            if rating >= csfd.RATING_THRESHOLD:
                extracted_films.append((film, rating))

            print(film.text, rating)
        except Exception as e:
            print(f'Exception occured for film {film.text}: {e}')

    print(f'--- FILMS ABOVE {csfd.RATING_THRESHOLD} ---')
    # import pdb; pdb.set_trace()

    for film, rating in extracted_films:
        time_and_channel = film.findPrevious(class_="time").text

        date_played = film.findPrevious(class_='selected').text.strip('\n')
        year = film.parent.find(class_='film-year').text

        film_type = film.parent.find(class_='film-type')

        if film_type and 'seri' in film_type.text:
            print(film_type.text)
            print(f'Skiping {film.text} because it is a {film_type.text}')

        # print(f'{film.text}: {rating} % \n{date_played}\n{time_and_channel}')
