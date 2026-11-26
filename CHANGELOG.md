# Changelog

## [1.0.1](https://github.com/wattnet/wattnet-api/compare/v1.0.0...v1.0.1) (2026-11-26)


### Features

* add an MCP interface next to the REST one ([#60](https://github.com/wattnet/wattnet-api/issues/60)) ([63232b4](https://github.com/wattnet/wattnet-api/commit/63232b476272683c2a90a3ae94a805c33b48d7a6))
* add points next to values in every series and deprecate values ([#55](https://github.com/wattnet/wattnet-api/issues/55)) ([0fff70e](https://github.com/wattnet/wattnet-api/commit/0fff70e0398352c20051a5ff7a6e77562ce72d94))
* add the resolution parameter to the series ([#58](https://github.com/wattnet/wattnet-api/issues/58)) ([46c194a](https://github.com/wattnet/wattnet-api/commit/46c194ab2bb426b2c899b4690780dd50ab99fe9b))
* add updated_at to the aggregates and a stable code to every error ([#56](https://github.com/wattnet/wattnet-api/issues/56)) ([f21380f](https://github.com/wattnet/wattnet-api/commit/f21380fad3cab4bf335ea56075782fb4fb2bd6dd))
* answer a query without a range with the latest data before now ([#63](https://github.com/wattnet/wattnet-api/issues/63)) ([7f7464b](https://github.com/wattnet/wattnet-api/commit/7f7464b0fea003b0ff4d598de0ffbf1bc8a22d5d))
* **api:** accept hydro_pumped_storage production type ([e6bebf8](https://github.com/wattnet/wattnet-api/commit/e6bebf83874f1bdf73ff560debebf953a1a99290))
* **api:** declare the HTTPBearer scheme in the OpenAPI document ([fdf6a92](https://github.com/wattnet/wattnet-api/commit/fdf6a927acaf7fe7d1c0f11cd651f72be47edcaa))
* **api:** declare the HTTPBearer scheme in the OpenAPI document ([42b97d6](https://github.com/wattnet/wattnet-api/commit/42b97d6b861b68273392044e3f0defced47d8d38))
* **api:** explain in the docs where to get a token, when the developer portal is configured ([e62a378](https://github.com/wattnet/wattnet-api/commit/e62a378861743f6f9cc420fa82637dad4ea6b31a))
* **api:** keep every status endpoint public in the docs ([61d15af](https://github.com/wattnet/wattnet-api/commit/61d15affc20505570533d792167b948899524cac))
* apply the access tiers to the data endpoints ([#45](https://github.com/wattnet/wattnet-api/issues/45)) ([b7b570d](https://github.com/wattnet/wattnet-api/commit/b7b570d081109aed0bb21fd9cacd410ea4e05ead))
* round the values in the API, where they are presented ([0f2b9d0](https://github.com/wattnet/wattnet-api/commit/0f2b9d0eb26c0cf97faa5cd2dbefecef6c07dc85))
* show the commit of a snapshot, or the package version, as the version of the API documentation ([#53](https://github.com/wattnet/wattnet-api/issues/53)) ([da64ca1](https://github.com/wattnet/wattnet-api/commit/da64ca11bc8dc385e13345841fa8837fd8828f8f))
* take wattnet-storage from git, read the table zone_mix and add the snapshot workflow ([7b396c4](https://github.com/wattnet/wattnet-api/commit/7b396c4329a38ea70782703fd6b8052270e8aa55))
* take wattnet-storage from git, read the table zone_mix and add the snapshot workflow ([2f0f0e4](https://github.com/wattnet/wattnet-api/commit/2f0f0e45187cc4aabfa1f5c89ae224cbb3dd38c9))
* tell the clients that they may reuse an answer with data for a minute ([#57](https://github.com/wattnet/wattnet-api/issues/57)) ([ac45756](https://github.com/wattnet/wattnet-api/commit/ac457566211ec018ce3ec7730040f834f08403b2))


### Bug Fixes

* **deps:** resolve Dependabot security alerts ([e8dc9ec](https://github.com/wattnet/wattnet-api/commit/e8dc9ecca18b885feb0557ea25fe69c619ba5d08))
* **deps:** resolve Dependabot security alerts ([198e426](https://github.com/wattnet/wattnet-api/commit/198e4268493ae9ce231febf7b196262e830740e9))
* do not count the list of zones and the factors as a query of every zone ([#49](https://github.com/wattnet/wattnet-api/issues/49)) ([bde766d](https://github.com/wattnet/wattnet-api/commit/bde766d640ad6d584f4a004dd7e27c3d5e80788f))
* improve the status endpoints, add the probes and run as non-root ([#44](https://github.com/wattnet/wattnet-api/issues/44)) ([9ac1b84](https://github.com/wattnet/wattnet-api/commit/9ac1b844d01cc3dc0f089471acdcbb47bd6ac769))
* refuse repeated, unknown and empty query parameters ([#50](https://github.com/wattnet/wattnet-api/issues/50)) ([c1d82cf](https://github.com/wattnet/wattnet-api/commit/c1d82cff813131403f9e78be1b0142dcde70e267))
* tell the version in the MCP server and do not serve subscriptions/listen ([#61](https://github.com/wattnet/wattnet-api/issues/61)) ([b27be96](https://github.com/wattnet/wattnet-api/commit/b27be96688ace70627ce842661243ed25d428695))
* wait up to 30 s for the external providers in the status checks ([#51](https://github.com/wattnet/wattnet-api/issues/51)) ([6bc3875](https://github.com/wattnet/wattnet-api/commit/6bc38758a5cd82ad12c34081d9bb1b339e39d44c))


### Performance Improvements

* ask the providers of the status at the same time ([#62](https://github.com/wattnet/wattnet-api/issues/62)) ([fa28955](https://github.com/wattnet/wattnet-api/commit/fa289553666fc15106c212d920b5dd3a19de2419))


### Documentation

* add the Conventional Commits badge ([22521ab](https://github.com/wattnet/wattnet-api/commit/22521ab9a088ac3e95e9a959c68423746f3570c4))
* align community files with the repository reference ([495bc82](https://github.com/wattnet/wattnet-api/commit/495bc8262b81c3d53cf92460e0dba8ec4494fdd9))
* align README funding section with other wattnet repos ([1ec19b7](https://github.com/wattnet/wattnet-api/commit/1ec19b7d53ec50d5d1aa5c3fa40eb41905b569f8))
* align README funding section with other wattnet repos ([5c1b9d9](https://github.com/wattnet/wattnet-api/commit/5c1b9d922b8abdb8d6c103acf5dd30128614bc1d))
* **api:** refresh Swagger description and funding logos ([e4b589c](https://github.com/wattnet/wattnet-api/commit/e4b589cc2c3560cb275d91f1a12cbe07d4c9ad3c))
* fix the Ruff badges so they render on GitHub ([e390cf7](https://github.com/wattnet/wattnet-api/commit/e390cf76b931f7f01beaf3e2c7bfb7635c57bc54))
* fix the Ruff badges so they render on GitHub ([ba08d34](https://github.com/wattnet/wattnet-api/commit/ba08d349bbf6dbe9164dd261f49d4d32f37325ef))
* point to the renamed wattnet-software-architecture repository ([ff6b4f2](https://github.com/wattnet/wattnet-api/commit/ff6b4f2b31fcad6da74b3b18aa7212c6cf663723))
* point to the renamed wattnet-software-architecture repository ([d04b323](https://github.com/wattnet/wattnet-api/commit/d04b32357add33c49b2165761304d95bb9376960))
* refresh the README badge table ([bbf54cc](https://github.com/wattnet/wattnet-api/commit/bbf54cc76faaad0fcc2b77bf621ff15c522c5f6c))
* replace Docker Compose section with docker run example ([700d0d5](https://github.com/wattnet/wattnet-api/commit/700d0d526f9b47293905813bcb2b8d54be3c0573))


### Build System

* **deps:** pin wattnet-storage to the commit that lets a client skip the schema bootstrap ([#48](https://github.com/wattnet/wattnet-api/issues/48)) ([a12df3d](https://github.com/wattnet/wattnet-api/commit/a12df3d05839ca7b895d71c20afcac0a41dccf32))
* **deps:** pin wattnet-storage to the commit that reads a year with less than half the memory ([#46](https://github.com/wattnet/wattnet-api/issues/46)) ([d3ed8fd](https://github.com/wattnet/wattnet-api/commit/d3ed8fd921833c70f74fd48032c88e82bccd10af))
* migrate linting and formatting to Ruff ([2595cb0](https://github.com/wattnet/wattnet-api/commit/2595cb09849215bc8292a85fb8a7eb678202d9ab))
* migrate to Ruff and refresh README badges ([cbdca63](https://github.com/wattnet/wattnet-api/commit/cbdca636463857b693b2c3aaf682f15c1d8f8c83))
* update the vulnerable dependencies and drop support for Python 3.10 ([#47](https://github.com/wattnet/wattnet-api/issues/47)) ([cb1aba6](https://github.com/wattnet/wattnet-api/commit/cb1aba618f906888712d0328317f1602cf02784f))


### Miscellaneous Chores

* release 1.0.1 ([731180a](https://github.com/wattnet/wattnet-api/commit/731180ac41d4a8d7f61f5c5e14af51790cc4cf9a))
