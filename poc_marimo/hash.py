import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    mo.md("""# hash 
    ## sekwa ?
    c super""")
    return


@app.cell
def _():
    import duckdb

    con = duckdb.connect()

    N = 5_000_000

    con.execute(f"""
        CREATE TABLE IF NOT EXISTS base AS
            SELECT
                'toto'||i AS id_string,
                i::UBIGINT AS id_int
            FROM range({N}) t(i);
            """)

    # print(con.sql("select count(*) from base"))
    con.sql("from base limit 10").pl()
    return (con,)


@app.cell
def _(con):
    import time
    import statistics


    def bench(sql, label, n=10):
        times = []
        for _ in range(n):
            t0 = time.time()
            r = con.sql(sql).fetchall()
            times.append(time.time() - t0)
            mean = statistics.fmean(times)
        print(f"{label:30s}: mean={mean*1000:7.1f} ms   -> {r}")
        return mean

    mean_string = bench("select count(*) from base A join base B using(id_string)", "join sur string")
    mean_int = bench("select count(*) from base A join base B using(id_int)", "join sur int")

    print(f"improvement : {(mean_string / mean_int)*100 - 100 : 7.1f}%")
    return


if __name__ == "__main__":
    app.run()
