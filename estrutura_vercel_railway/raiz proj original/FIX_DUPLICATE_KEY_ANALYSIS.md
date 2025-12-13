# Fix: Duplicate Key Error in Multi-Agent Analysis Saving

## Problem Summary
You were encountering a PostgreSQL `UniqueViolation` error when trying to save a multi-agent analysis:

```
Erro ao salvar: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint 
"validacao_multi_agente_analise_hash_sha256_key" 
DETAIL: Key (hash_sha256)=(92d71d8a379e18e3fdac4c26968159549601519d7d2689d98dbbafacc0c8802f) already exists.
```

## Root Cause
The system generates a unique SHA-256 hash for each analysis based on:
- Document content
- Timestamp (milliseconds)
- UUID

When you tried to save the same analysis twice (either by clicking the save button multiple times or re-analyzing the same document), the system attempted to create a new record with a hash that already existed in the database, violating the unique constraint.

## Solution Implemented

### Backend Changes (`scripts/apis/multi_agent/api_validacao_multi_agente.py`)

1. **Duplicate Detection**: Before saving, the system now checks if an analysis with the same hash already exists:
   ```python
   analise_existente = ValidacaoMultiAgenteAnalise.obter_por_hash(analise.hash_sha256)
   ```

2. **User-Specific Handling**: 
   - If the analysis belongs to the **same user**, it returns the existing analysis information with a message: "Esta análise já foi salva anteriormente"
   - If it belongs to a **different user**, it generates a new hash with an additional random salt to ensure uniqueness

3. **Graceful Response**: Instead of crashing with an error, the system now returns success with the existing analysis details, including a flag `ja_existia: true`

### Frontend Changes (`static/js/salvamento_validacao_multi_agente.js`)

1. **New Warning Notification**: Added `mostrarNotificacaoAviso()` function to display a warning when an analysis already existed

2. **Conditional Messaging**: The frontend now checks if `resultado.data.ja_existia` is true and shows an appropriate message:
   - ✅ Success notification for new saves
   - ℹ️ Warning notification for duplicate saves (already existed)

3. **Consistent User Experience**: Both cases redirect to the history page, ensuring smooth workflow

## Benefits

1. **No More Crashes**: The system handles duplicates gracefully instead of throwing errors
2. **Better User Experience**: Clear messaging about whether the analysis was newly saved or already existed
3. **Data Integrity**: Prevents duplicate data while allowing multiple users to analyze the same document
4. **Idempotent Operations**: Clicking "Save" multiple times won't cause errors

## Testing Recommendations

1. Save an analysis once - should see success message
2. Try to save the same analysis again - should see "already saved" warning
3. Verify that both cases redirect to the history page correctly
4. Check that the existing analysis details are displayed correctly

## Files Modified

- `app.py` (line 15250-15344) - Fixed main endpoint with duplicate detection
- `scripts/apis/multi_agent/api_validacao_multi_agente.py` - Blueprint endpoint with duplicate detection  
- `static/js/salvamento_validacao_multi_agente.js` - Frontend warning notifications

## Important Notes

The application had TWO endpoints handling the same route `/api/validacao-multi-agente/salvar`:
1. **Main endpoint in `app.py`** (this was the one being called)
2. **Blueprint endpoint in API file** (not being reached)

Both have now been updated with the same duplicate detection logic to ensure consistency.
