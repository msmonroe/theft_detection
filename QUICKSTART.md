# Quick Start Guide - Theft Detection System

## Running Without Azure Credentials (Demo Mode)

You can run the system immediately without any Azure setup!

### Option 1: Automatic Demo Mode

Just run the script - it will automatically detect missing credentials and switch to demo mode:

```bash
python retail_theft_detection.py
```

### Option 2: Explicit Demo Mode

Create or edit `.env` file:

```ini
DEMO_MODE=true
```

Then run:

```bash
python retail_theft_detection.py
```

## What Demo Mode Does

✅ Creates a sample store image (`demo_store.jpg`)  
✅ Simulates person detection with 92% confidence  
✅ Simulates object detection (bag)  
✅ Runs full detection pipeline with mock data  
✅ Generates analysis report (`demo_report.json`)  
✅ No Azure account or API calls required  
✅ No costs incurred  

## Switching to Azure AI Vision (Production Mode)

When you have Azure credentials:

1. **Get Azure Credentials**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a Computer Vision resource
   - Navigate to: Resource → Keys and Endpoint
   - Copy your Endpoint URL and Key

2. **Update `.env` file**:

   ```ini
   AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_VISION_KEY=your-32-character-key-here
   DEMO_MODE=false
   ```

3. **Run the system**:

   ```bash
   python retail_theft_detection.py
   ```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEMO_MODE` | No | Set to `true` for demo mode (default: `false`) |
| `AZURE_VISION_ENDPOINT` | Yes* | Azure Computer Vision endpoint URL |
| `AZURE_VISION_KEY` | Yes* | Azure Computer Vision subscription key |

*Required only when `DEMO_MODE=false` or not set

## Testing the System

Run the complete test suite:

```bash
pytest test_theft_detection.py -v
```

All 16 tests should pass with or without Azure credentials.

## Generated Files

When you run the system, it creates:

- `demo_store.jpg` - Sample store scene image (demo mode)
- `demo_report.json` - Analysis report (demo mode)
- `theft_report.json` - Real analysis report (Azure mode)
- `logs/` - Application logs directory

## Security Note

⚠️ **Never commit your `.env` file to version control!**

The `.env` file contains sensitive credentials. The `.gitignore` file is configured to exclude it automatically.

Always use `.env.example` as a template and keep your actual `.env` file private.

## Next Steps

1. ✅ Run demo mode to understand the system
2. ✅ Review `demo_report.json` and `demo_store.jpg`
3. ✅ Run unit tests to verify installation
4. 📝 Get Azure credentials when ready
5. 🚀 Switch to production mode for real detection

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'dotenv'`  
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Problem**: Permission errors when running tests  
**Solution**: Tests automatically handle Windows file locking issues

**Problem**: Want to test without Azure but have credentials set  
**Solution**: Set `DEMO_MODE=true` in `.env` file

## Support

For issues or questions:
- Check the main README.md for full documentation
- Review LOGGING_GUIDE.md for logging details
- Run tests to verify your setup: `pytest test_theft_detection.py -v`
