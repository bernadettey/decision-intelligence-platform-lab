CREATE TABLE IF NOT EXISTS business_units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    region VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS cost_centres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    business_unit_id INTEGER NOT NULL REFERENCES business_units(id)
);

CREATE TABLE IF NOT EXISTS actuals (
    id SERIAL PRIMARY KEY,
    period DATE NOT NULL,
    business_unit_id INTEGER NOT NULL REFERENCES business_units(id),
    cost_centre_id INTEGER NOT NULL REFERENCES cost_centres(id),
    revenue NUMERIC(14, 2) NOT NULL,
    cogs NUMERIC(14, 2) NOT NULL,
    opex NUMERIC(14, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    period DATE NOT NULL,
    business_unit_id INTEGER NOT NULL REFERENCES business_units(id),
    cost_centre_id INTEGER NOT NULL REFERENCES cost_centres(id),
    revenue NUMERIC(14, 2) NOT NULL,
    cogs NUMERIC(14, 2) NOT NULL,
    opex NUMERIC(14, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    period DATE NOT NULL,
    business_unit_id INTEGER NOT NULL REFERENCES business_units(id),
    cost_centre_id INTEGER NOT NULL REFERENCES cost_centres(id),
    revenue NUMERIC(14, 2) NOT NULL,
    cogs NUMERIC(14, 2) NOT NULL,
    opex NUMERIC(14, 2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_actuals_period ON actuals(period);
CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period);
CREATE INDEX IF NOT EXISTS idx_forecasts_period ON forecasts(period);
