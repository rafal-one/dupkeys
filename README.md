# dupkeys

Find duplicate keys in JSON, `.env` and INI/properties files. Parsers (`json.load`, `jq`, dotenv, configparser variants) silently keep the **last** value, so a copy-pasted key quietly overrides the one you meant. Stdlib only, Python 3.9+.

## Usage
```console
$ dupkeys config.json .env settings.ini
config.json: duplicate key 'timeout' (last value wins)
.env:4: duplicate key 'API_URL' (first at line 1; last value wins)
settings.ini:9: duplicate key '[db] host' (first at line 6; last value wins)
```
Type is guessed from the name (`*.json`, `.env*`, otherwise INI/properties); override with `--type json|env|ini`. Exit code 0 clean, 1 duplicates found, 2 unreadable/invalid file. Works as a pre-commit/CI step. Not checked: YAML, TOML (TOML parsers already reject duplicates).

## pre-commit
```yaml
- repo: https://github.com/rafal-one/dupkeys
  rev: v0.1.0
  hooks:
    - id: dupkeys
```
(Tag `v0.1.0` is created when the PyPI release is published; until then use `rev: main`.)

## Install
`pip install dupkeys` (once published) or copy `dupkeys.py`.

## Support
MIT licensed. If it saves you time: https://paypal.me/RafalBaranowski
