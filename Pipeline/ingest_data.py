import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL username')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default='5432', help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2021, type=int, help='Year of the data')
@click.option('--month', default=1, type=int, help='Month of the data')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for ingestion')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def main(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table):

    print("Starting ingestion...")
    
    print(
        f"""
        PostgreSQL:
        user={pg_user}
        host={pg_host}
        port={pg_port}
        database={pg_db}

        Dataset:
        year={year}
        month={month}
        table={target_table}
        """
    )

    # Create URL
    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"
    url = f"{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz"

    # Create engine
    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    # Read CSV in chunks
    df_iter = pd.read_csv(
        url,
        iterator=True,
        chunksize=chunksize
    )

    first = True

    for df_chunk in tqdm(df_iter):

        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace"
            )
            first = False
            print("Table created")

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )

        print(f"Inserted {len(df_chunk)} rows")


if __name__ == '__main__':
    main()