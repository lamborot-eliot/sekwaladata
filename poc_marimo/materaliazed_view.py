import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb

    con = duckdb.connect()
    return con, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # les vues matérialisées
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## table clients (modifiable)
    """)
    return


@app.cell
def _():
    import polars as pl

    customers = pl.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "name": [
            "Alice Martin",
            "Ben Carter",
            "Chloe Dubois",
            "David Kim",
            "Elena Rossi",
        ],
        "email": [
            "alice.martin@example.com",
            "ben.carter@example.com",
            "chloe.dubois@example.com",
            "david.kim@example.com",
            "elena.rossi@example.com",
        ],
        "update_date": [
            "2026-08-25",
            "2024-10-19",
            "1023-12-10",
            "1026-03-16",
            "1025-05-19"
        ],
    })

    customers = customers.with_columns(
        pl.col("update_date").str.to_date("%Y-%m-%d")
    )
    return customers, pl


@app.cell
def _(customers, mo):
    editor_customers = mo.ui.data_editor(customers)
    editor_customers
    return (editor_customers,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## table factures (modifiable)
    """)
    return


@app.cell
def _(pl):

    invoices = pl.DataFrame({
        "invoice_id": [1, 2, 3, 4, 5],
        "amount": [
            123,
            67,
            544,
            2801,
            1000,
        ],
        "date": [
            "2026-08-25",
            "2024-10-19",
            "2023-12-10",
            "2026-03-16",
            "2025-05-19"
        ],
        "customer_id": [1, 1, 2, 6, 7],
    })

    invoices = invoices.with_columns(
        pl.col("date").str.to_date("%Y-%m-%d")
    )
    return (invoices,)


@app.cell
def _(invoices, mo):
    editor_invoices = mo.ui.data_editor(invoices)
    editor_invoices
    return (editor_invoices,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## vue (en direct) sur la jointure entre ces deux tables
    """)
    return


@app.function
def style_cell(row_id, column_name, value):
    if column_name != "customer_id":  # change to your column name
        return {}

    colors = {
        1: "sandybrown",
        2: "darkgreen",
        3: "lightcoral",
        4: "mediumseagreen",
        5: "firebrick",
        6: "khaki",
        7: "yellowgreen",
        8: "salmon",
        9: "seagreen",
        10: "indianred",
    }

    return {
        "backgroundColor": colors.get(value, "white"),
        "color": "black",
    }


@app.cell
def _(customers, editor_customers, editor_invoices, invoices):
    # tricks to have the updated df as a new variable and auto trigger refresh
    invoices_updated = editor_invoices.value if editor_invoices.value is not None else invoices
    customers_updated = editor_customers.value if editor_customers.value is not None else customers


    join_df = customers_updated.join(invoices_updated, on='customer_id').sort(by='customer_id')

    join_df

    # table = mo.ui.table(data=join_df, style_cell=style_cell)
    # table
    return customers_updated, invoices_updated


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Matérialisation

    Imaginons maintenant que l'on veuille materialiser cette vue toutes les heures, on peut simplement faire :
    ``` sql
    CREATE TABLE materialized as SELECT * FROM my_view;
    ```

    **TODO display table**

    Cependant, avec cette solution il faut recalculer la vue entièrement et réécrire l'entièreté de la table toutes les heures. Si les tables sont assez volumineuses, ces opérations peuvent être couteuses.

    Une autre solution pour s'eviter de tout réécrire est d'utiliser l'instruction **MERGE** en ne réécrivant que les nouvelles lignes.

    ``` sql
    MERGE INTO materialized
        USING (SELECT * from my_view) AS v
        ON (v.invoice_id = materialized.invoic_id)
        WHEN NOT MATCHED THEN INSERT;
    ```

    **TODO display table**

    Il reste deux problèmes, premièrement il faut encore recalculer entièrement la vue à chaque refresh.
    Deuxiemement, si une ligne déja inséré change, la mise-à-jour ne sera pas faite.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Différentes facons de faires
    ## la version GREATEST()
    """)
    return


@app.cell
def _(con):
    con.sql("""CREATE OR REPLACE TABLE materialized as SELECT *, greatest(invoices_updated.date, customers_updated.update_date) as max_date FROM invoices_updated join customers_updated using (customer_id);""")
    con.sql("from materialized")
    return


@app.cell
def _(con):
    max_date = con.sql("select max(max_date) from materialized").fetchall()[0][0]
    max_date = max_date.strftime("%Y-%m-%d")
    max_date
    return (max_date,)


@app.cell
def _(con, customers_updated, invoices_updated, max_date, mo):
    con.register("invoices_updated_df", invoices_updated,)
    con.register("customers_updated_df", customers_updated)


    con.sql("create or replace table invoices_updated as select * from invoices_updated_df")
    con.sql("create or replace table customers_updated as select * from customers_updated_df")

    query_greatest = f"""EXPLAIN (FORMAT mermaid) select *, greatest(invoices_updated.date, customers_updated.update_date) as max_date from invoices_updated join customers_updated using (customer_id)
    where max_date > cast({max_date} as DATE) """

    mo.mermaid(con.sql(query_greatest).fetchall()[0][1])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## La version union des diff
    """)
    return


@app.cell
def _(con, max_date):
    con.sql(f"""select * from invoices_updated
        where invoices_updated.date > cast('{max_date}' as DATE)""")
    return


@app.cell
def _(con, customers_updated, invoices_updated, max_date, mo):
    con.register("invoices_updated_df", invoices_updated,)
    con.register("customers_updated_df", customers_updated)


    con.sql("create or replace table invoices_updated as select * from invoices_updated_df")
    con.sql("create or replace table customers_updated as select * from customers_updated_df")

    query_union_diff = f"""

    EXPLAIN (FORMAT mermaid) 
    select * from invoices_updated join customers_updated using (customer_id)
    where invoices_updated.date > cast('{max_date}' as DATE)
    union
    select * from invoices_updated join customers_updated using (customer_id)
    where customers_updated.update_date > cast('{max_date}' as DATE)"""

    # con.sql(query_union_diff).pl()

    print(con.sql(query_union_diff).fetchall()[0][1])
    mo.mermaid(con.sql(query_union_diff).fetchall()[0][1])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## La version OR
    """)
    return


@app.cell
def _(con, customers_updated, invoices_updated, max_date, mo):
    con.register("invoices_updated_df", invoices_updated,)
    con.register("customers_updated_df", customers_updated)


    con.sql("create or replace table invoices_updated as select * from invoices_updated_df")
    con.sql("create or replace table customers_updated as select * from customers_updated_df")

    query_or = f"""
    EXPLAIN (FORMAT mermaid) 

    select * from invoices_updated join customers_updated using (customer_id)
    where invoices_updated.date > cast('{max_date}' as DATE)
    OR customers_updated.update_date > cast('{max_date}' as DATE)
    """


    # con.sql(query_or).pl()

    print(con.sql(query_or).fetchall()[0][1])
    mo.mermaid(con.sql(query_or).fetchall()[0][1].replace('\\"', ""))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## La version "Driving ID"
    """)
    return


@app.cell
def _(con, customers_updated, invoices_updated, max_date, mo):
    con.register("invoices_updated_df", invoices_updated,)
    con.register("customers_updated_df", customers_updated)


    con.sql("create or replace table invoices_updated as select * from invoices_updated_df")
    con.sql("create or replace table customers_updated as select * from customers_updated_df")


    query_driving_id = f"""

    --EXPLAIN ANALYZE
    EXPLAIN (FORMAT mermaid)

    -- 1. Find the IDs of everything that changed in A
    WITH changed_from_a AS (
        SELECT customer_id as id
        FROM customers_updated 
        WHERE update_date > cast('{max_date}' as DATE)
    ),

    -- 2. Find the IDs of A based on what changed in B
    changed_from_b AS (
        SELECT customer_id AS id 
        FROM invoices_updated 
        WHERE date > cast('{max_date}' as DATE)
    ),

    -- 3. Combine the IDs (UNION is fast here because it's just one column)
    all_changed_ids AS MATERIALIZED (
        SELECT id FROM changed_from_a
        UNION
        SELECT id FROM changed_from_b
    )

    -- 4. Do the heavy join ONLY on the rows that actually changed
    SELECT 
        *
    FROM customers_updated A
    JOIN invoices_updated B 
      ON A.customer_id = B.customer_id
    INNER JOIN all_changed_ids c 
      ON A.customer_id = c.id
    """


    # con.sql(query_driving_id).pl()

    print(con.sql(query_driving_id).fetchall()[0][1])
    mo.mermaid(con.sql(query_driving_id).fetchall()[0][1].replace('\\"', ""))
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## conclusion: impossible de choper les diff des deux tables sans faire un full scan de chaque
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Parquet optimizations (to move)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Partitioning
    """)
    return


@app.cell
def _(con):
    print(con.sql("explain analyze select * from read_parquet('test') where id == 1 ").fetchall()[0][1])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Row group skipping
    """)
    return


@app.cell
def _(con):
    # 1. Create a dummy Parquet file with 100,000 rows
    # We force a small row_group_size (10,000) to create exactly 10 row groups.
    con.execute("""
        CREATE TABLE IF NOT EXISTS temp_table AS 
        SELECT range AS id, 'value_' || range::VARCHAR AS val 
        FROM range(1, 100001);
    """)
    con.execute("COPY temp_table TO 'test.parquet' (FORMAT PARQUET, ROW_GROUP_SIZE 10000);")

    # 2. Run EXPLAIN ANALYZE with a filter (id > 85000)
    # This filter should skip the first 8 row groups (0 to 80,000) entirely.
    query = "SELECT * FROM 'test.parquet' WHERE id > 85000"
    plan = con.execute(f"EXPLAIN ANALYZE {query}").fetchall()[0][1]

    print(plan)
    return


@app.cell
def _():
    import pyarrow.parquet as pq

    def analyze_row_group_pruning(file_path, filter_col, operator, threshold):
        parquet_file = pq.ParquetFile(file_path)
        metadata = parquet_file.metadata

        total_groups = metadata.num_row_groups
        kept = []
        skipped = []

        for i in range(total_groups):
            row_group = metadata.row_group(i)

            # Locate the targeted column
            for j in range(row_group.num_columns):
                column = row_group.column(j)

                if column.path_in_schema == filter_col:
                    stats = column.statistics

                    if not stats or not stats.has_min_max:
                        kept.append((i, "No statistics available (must scan)"))
                        continue

                    # Replicate the pruning decision logic
                    should_skip = False
                    reason = ""

                    if operator == ">":
                        if stats.max <= threshold:
                            should_skip = True
                            reason = f"Max value ({stats.max}) is <= threshold ({threshold})"
                    elif operator == "<":
                        if stats.min >= threshold:
                            should_skip = True
                            reason = f"Min value ({stats.min}) is >= threshold ({threshold})"
                    elif operator == "==":
                        if threshold < stats.min or threshold > stats.max:
                            should_skip = True
                            reason = f"Threshold ({threshold}) is outside range [{stats.min}, {stats.max}]"

                    if should_skip:
                        skipped.append((i, reason))
                    else:
                        kept.append((i, f"Range [{stats.min}, {stats.max}] overlaps with filter"))

        # Print the detailed analysis
        print(f"--- PRUNING ANALYSIS FOR {file_path} ---")
        print(f"Filter: {filter_col} {operator} {threshold}\n")
        print(f"Total Row Groups: {total_groups}")
        print(f"Row Groups Skipped: {len(skipped)}")
        print(f"Row Groups Kept: {len(kept)}\n")

        print("Detailed Decisions:")
        for rg_id, reason in skipped:
            print(f"  Row Group {rg_id:2d} -> SKIPPED: {reason}")
        for rg_id, reason in kept:
            print(f"  Row Group {rg_id:2d} -> KEPT   : {reason}")

    # Run the analysis on your file
    analyze_row_group_pruning("test.parquet", filter_col="id", operator=">", threshold=85000)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Column min/max (TODO)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ordering (TODO)
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
