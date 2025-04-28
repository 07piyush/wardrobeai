# PostgreSQL Setup Script
$ErrorActionPreference = "Stop"

# PostgreSQL paths
$POSTGRES_BIN = "D:\Prerequisites\postgreSQL\bin"
$POSTGRES_DATA = "D:\Prerequisites\postgreSQL\data"

# Database configuration
$DB_NAME = "wardrobe"
$DB_USER = "wardrobe_user"
$DB_PASSWORD = "wardrobe_password"
$SUPERUSER = "sharm"  # Using Windows username as superuser

# Add PostgreSQL bin to PATH if not already there
$env:Path = "$POSTGRES_BIN;$env:Path"

# Function to check if PostgreSQL is running
function Test-PostgresRunning {
    $pg_ctl = Join-Path $POSTGRES_BIN "pg_ctl.exe"
    & $pg_ctl status -D $POSTGRES_DATA
    return $LASTEXITCODE -eq 0
}

# Function to start PostgreSQL
function Start-Postgres {
    Write-Host "Starting PostgreSQL server..."
    $pg_ctl = Join-Path $POSTGRES_BIN "pg_ctl.exe"
    & $pg_ctl start -D $POSTGRES_DATA
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start PostgreSQL server"
    }
    Write-Host "PostgreSQL server started successfully"
}

# Function to create database and user
function Initialize-Database {
    Write-Host "Creating database and user..."
    
    # Create user
    & psql -U $SUPERUSER -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "User might already exist, continuing..."
    }
    
    # Create database
    & psql -U $SUPERUSER -d postgres -c "CREATE DATABASE $DB_NAME;"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Database might already exist, continuing..."
    }
    
    # Grant privileges
    & psql -U $SUPERUSER -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to grant privileges"
    }
    
    Write-Host "Database and user created successfully"
}

# Main execution
try {
    # Check if PostgreSQL is running
    if (-not (Test-PostgresRunning)) {
        Start-Postgres
    } else {
        Write-Host "PostgreSQL server is already running"
    }
    
    # Initialize database
    Initialize-Database
    
    Write-Host "`nPostgreSQL setup completed successfully!"
    Write-Host "Database: $DB_NAME"
    Write-Host "User: $DB_USER"
    Write-Host "Password: $DB_PASSWORD"
    Write-Host "`nUpdate your .env file with these credentials"
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} 