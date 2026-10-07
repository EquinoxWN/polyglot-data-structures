# OSV-Scanner (https://google.github.io/osv-scanner/) checks every resolved Maven dependency.
OSV ?= osv-scanner

.PHONY: setup lint test vectors bench ci audit

setup:
	cd python && python -m pip install -e ".[dev]"

lint:
	python spec/generate_vectors.py --check
	cd java && mvn -B -q -DskipTests compile
	cd python && python -m ruff check . ../spec && python -m ruff format --check . ../spec
	cd js && for f in src/*.js test/*.js; do node --check "$$f" || exit 1; done

test:
	cd java && mvn -B -q verify
	cd python && python -m pytest -q
	cd js && node --test

# Regenerate spec/vectors/*.json from the reference models.
vectors:
	python spec/generate_vectors.py

bench:
	@echo "M2: JMH, pyperf and mitata benchmarks land with the property tests"

# Known vulnerabilities in Python and Maven dependencies.
audit:
	cd python && python -m pip_audit --skip-editable
	cd java && mvn -B -q org.cyclonedx:cyclonedx-maven-plugin:2.9.3:makeAggregateBom -DoutputFormat=json -DoutputName=bom -DincludeTestScope=true
	$(OSV) scan source -L java/target/bom.json

ci: setup lint test
