# MTG Price Tracker

## Component Details

### 1. Main Entry Point (`main.py`)
- Simple entry point that launches the Textual app
- Minimal code for easy execution

### 2. Main Application (`src/app.py`)
**Responsibilities:**
- Initialize database and API connections
- Manage application state
- Handle user interactions (keyboard shortcuts, button clicks)
- Coordinate between widgets and data sources
- Price checking and change detection

**Key Methods:**
- `check_prices()`: Fetches current prices and compares with stored values
- `load_watchlist()`: Loads cards from database and updates UI
- `update_log_message()`: Displays price change notifications

### 3. Database Module (`src/database/db.py`)
**Schema:**
- `watchlist`: Card tracking (name, ID, price, timestamps)
- `price_history`: Historical price records
- `app_metadata`: Last check timestamp and settings

**Key Operations:**
- `add_card()`: Add new card to watchlist
- `update_price()`: Update price and record history
- `get_watchlist()`: Retrieve all tracked cards
- `get_last_check()`: Get last price check timestamp

### 4. Scryfall API (`src/api/scryfall.py`)
**Endpoints Used:**
- `/cards/search`: Search for cards by name
- `/cards/named`: Get exact card match
- `/cards/{id}`: Get card by Scryfall ID

**Features:**
- HTTP client with timeout handling
- Price extraction (USD → EUR → USD foil fallback)
- Error handling for network issues

### 5. Widgets (`src/widgets/`)

#### WatchlistWidget
- Displays tracked cards in a DataTable
- Shows: Name, Set, Price, Last Updated
- Supports row selection for deletion

#### SearchWidget
- Search input field
- Results displayed in DataTable
- Shows: Name, Set, Type, Price, Add action
- Emits CardSelected message for adding to watchlist

## Data Flow

### Startup Flow
```
1. App starts → Initialize DB & API
2. Load watchlist from database
3. Fetch current prices from Scryfall
4. Compare with stored prices
5. Log changes since last run
6. Display watchlist with updated prices
```

### Search Flow
```
1. User enters search query
2. Submit to Scryfall API
3. Parse results (max 10)
4. Display in SearchWidget table
5. User selects card
6. Add to database
7. Refresh watchlist display
```

### Price Update Flow
```
1. Triggered on startup or manual refresh
2. For each card in watchlist:
   a. Fetch current price from Scryfall
   b. Compare with stored price
   c. If changed: record in price_history
   d. Update current_price in watchlist
3. Generate change report
4. Update UI with new prices
```

## Technology Stack

- **Framework**: Textual (Python TUI framework)
- **Database**: SQLite3 (lightweight, file-based)
- **HTTP Client**: httpx (async-capable HTTP requests)
- **API**: Scryfall REST API (free, no auth required)

## Design Patterns

1. **Separation of Concerns**
   - UI logic in widgets
   - Data access in database module
   - API interactions in separate module

2. **Message Passing**
   - Widgets emit messages for parent app to handle
   - Loose coupling between components

3. **State Management**
   - Database is source of truth
   - UI reflects database state
   - Prices updated in database first, then UI

## Future Extension Points

1. **Additional Widgets**
   - Add new widgets to `src/widgets/`
   - Import in app.py and add to layout

2. **More API Sources**
   - Create new API modules in `src/api/`
   - Implement same interface pattern

3. **Enhanced Database**
   - Add tables for collections, trades, etc.
   - Extend Database class with new methods

4. **Export Features**
   - Add export methods to Database class
   - Create export utility in `src/utils/`

## Error Handling

- **Network Errors**: Caught in API module, returns empty/None
- **Database Errors**: SQLite exceptions handled in Database class
- **Missing Data**: Graceful degradation (show "N/A" for missing prices)

## Performance Considerations

- **Batch Processing**: All price updates done in single pass
- **Efficient Queries**: Indexed database lookups
- **Rate Limiting**: Respectful API usage (sequential requests)
- **Caching**: Database serves as price cache

## Security Notes

- No API keys required (Scryfall is open)
- Local database only (no remote connections)
- No user authentication needed
- SQLite injection prevented by parameterized queries

