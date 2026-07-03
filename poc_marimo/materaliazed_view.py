import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb

    con = duckdb.connect()
    return (mo,)


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
    })
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
    return


if __name__ == "__main__":
    app.run()
