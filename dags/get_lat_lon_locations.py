from airflow.decorators import dag, task
from datetime import timedelta

@dag(
    dag_id = "get_locations_lat_lon",
    start_date = None,
    schedule = None,
    catchup = None,
)
def get_locations():
    @task(
        retries = 3,
        retry_delay = timedelta(minutes=3)
    )
    def get_location():
        from include.get_locations_lat_lon import get_coordinates
        locations = ["Jakarta Barat", "Jakarta Pusat", "Jakarta Selatan", "Jakarta Timur", "Jakarta Utara"]
        get_coordinates(locations)

    get_location()

get_locations()