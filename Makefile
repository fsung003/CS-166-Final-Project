.PHONY: all db init run clean

all: init run

# Database connection settings
DB_HOST= 127.0.0.1
DB_PORT= 32237
DB_USER= ali229
DB_NAME= ali229_DB

# SQL files to execute
SQL_FILES=schema.sql populate.sql

# Run SQL initialization files
init:
	@echo "Waiting for database..."
	@until pg_isready -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER); do \
		sleep 1; \
	done

	@echo "Running SQL files..."
	@for file in $(SQL_FILES); do \
		echo "Executing $$file"; \
		psql -h $(DB_HOST) -U $(DB_USER) -d $(DB_NAME) -f $$file; \
	done

# Start application
run:
	@echo "Starting application..."
	python3 main.py

clean:
	@echo "Cleaning up..."