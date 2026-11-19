# T0 Binance USD-M BTCUSDT archive payload validation — 2026-11-20

## Scope and approval

Owner-approved bounded retrieval and validation only. Source partition:
- Monthly ZIP + `.CHECKSUM`: BTCUSDT M15/H1, 2020-01 through 2026-10.
- Daily ZIP + `.CHECKSUM`: BTCUSDT M15/H1, 2019-12-31 and 2026-11-01 through 2026-11-18.
- Daily fallback for defects in monthly objects was not invoked; no monthly defects were found.
- No REST tail, SQLite creation/write, Dropbox, VPS/runtime, feeder/writer, deployment, restore or cutover.

## Retrieval budget

- S3-compatible ListObjectsV2 metadata was enumerated with pagination before download.
- Objects: 404 total = 202 ZIP + 202 checksum sidecars.
- Aggregate listed and downloaded size: 14,929,033 bytes (ZIP 14,922,117 bytes; checksum sidecars 6,916 bytes), below the approved 100 MiB cap.
- Staging: isolated Firecrawl execution environment, `/tmp/t0-archive-validation`; source ZIP and sidecars retained there during validation.
- Source bucket: `https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/`.

## Validation results

**PASS — payload validation**

| Check | Result |
|---|---|
| ZIP objects / sidecars | 202 / 202 |
| SHA-256 sidecar comparisons | 202/202 PASS |
| ZIP CRC / single CSV / 12-column structure | 202/202 PASS |
| Candle rows | M15 241,440; H1 60,360 |
| Header handling | 76 archives with header; 126 without |
| Intra-archive timestamp gaps | 0 |
| Inter-archive timestamp gaps | 0 |
| Duplicate or out-of-order timestamps | 0 |
| OHLC / numeric anomalies checked | 0 |
| Errors in final validation pass | 0 |

### Coverage observed in retrieved payloads

| Timeframe | First open UTC | Last open UTC | Rows | Continuous expected rows |
|---|---|---|---:|---:|
| M15 | 2019-12-31 00:00 | 2026-11-18 23:45 | 241,440 | 241,440 |
| H1 | 2019-12-31 00:00 | 2026-11-18 23:00 | 60,360 | 60,360 |

Each timeframe contains 82 monthly archives and 19 daily archives. Every archive's filename period/date matched its first and last candle timestamps. Every candle's open/close interval was checked against its timeframe. All rows were ordered and contiguous within archives and across the selected source partition.

This validates the downloaded archive payloads only. It does not establish that Binance has no earlier history outside the selected archive interface, nor does it validate candles after 2026-11-18. The current tail through the retrieval cutoff is not covered. No daily/monthly overlap payloads were downloaded for duplicate/conflict comparison because the approved partition selected disjoint periods; therefore overlap conflict comparison is NOT APPLICABLE to this retrieval batch.

## Per-object provenance manifest

The SHA-256 below is the hash of each downloaded ZIP payload and matched the digest in its paired `.CHECKSUM` object. The paired sidecar key is the ZIP key plus `.CHECKSUM`.

### Daily M15 (19 ZIP)

| S3 object key | Bytes | SHA-256 | Rows |
|---|---:|---|---:|
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2019-12-31.zip` | 4678 | `7ea064f87f2cb0d8ef568fa1ad2e6ffae9b6d86210ea1ef21b077324e0abf0ab` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-01.zip` | 4863 | `e4b7f8eca66e16677db552806a3e5c03fafff2918ce4c424d500e3cf8bc062a5` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-02.zip` | 5057 | `c49c17262c4ff70339aa7c466118a9de35b792f3d436419d23c5681a5e51a51e` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-03.zip` | 5025 | `2383ef685a08af4d97d533cb33de6eef1c9d34d7144471facea42604a0af8738` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-04.zip` | 5159 | `84b71aab00827b8b6526ea0719aeef8c284290ea37d7972ee2df3b1d05dc4077` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-05.zip` | 5121 | `bd2909fa2d8b4e88c16ef2ab3556b296c5e4efcf75f0f672be74d788f7c4350e` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-06.zip` | 5066 | `cd7f0a766ebda18258eb41b5964cc756b9b6444fc2cc7d1c1bd69a394060a301` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-07.zip` | 4777 | `134a223783f78795bb6f17544f1c3d7dd619ea11f5cc3ed166d78d06dfa2efab` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-08.zip` | 4801 | `1701e8c5186c399c45713ebef47db10651206850fe0840fabfa99cd00300de63` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-09.zip` | 5132 | `da6266372f57a6d56652ffceefe42f134c8cf51176daa512c314fcf3165a3a82` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-10.zip` | 5046 | `1631882a3307faa0557adf82fdb82aba34bdfa7b7da85410657bd68903848382` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-11.zip` | 5071 | `61147becda750fe2821f9fc5001845d7bf747cfa1acf9f0c03f7aa7229f2da5a` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-12.zip` | 5045 | `e9b872a383a358c0371cb6459e492a17bc7f5a4d123046d0a668fabb3013904f` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-13.zip` | 5198 | `f00151cbba9be9573a7404002e7daf78b2ebb1e35e8b10f5894d5ef7135879a5` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-14.zip` | 5179 | `9f251031043abe70e73941f3edbbe0476913584b936313c9011458b08b14c936` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-15.zip` | 5166 | `fd381f287742d9dc59893adc9fa2daae422a83266cb64a245cd9c98456550779` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-16.zip` | 5152 | `ec5b11a61f6aa99727c85192dd974851163ea563f02df1c9abf06d34efe5ea79` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-17.zip` | 5155 | `615b1360e0077c309251be03b6b3926f404a06c7039463f19f4ebd2b437be1ba` | 96 |
| `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2026-11-18.zip` | 5116 | `48fd447a712024176a02b651e4b8a09544d6d5f8b5e1f63ca4a882c8cf4885f7` | 96 |

### Daily H1 (19 ZIP)

| S3 object key | Bytes | SHA-256 | Rows |
|---|---:|---|---:|
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2019-12-31.zip` | 1387 | `8ad8402a2b7eb92d48a3613fcea783592d7fec9c99dc07613271589501a1701a` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-01.zip` | 1513 | `f01880922915ec6d860a1516c47dc10811c0fc2be01f829cd6bf2d66f1622e8b` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-02.zip` | 1551 | `787798e65210de5a7bf63507e1fc5eca028cbc458f7f351e9939277820946475` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-03.zip` | 1550 | `d62cfdb2d8c25f257121ed3936665298a4806e8680a12552d84cce707a83a232` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-04.zip` | 1583 | `232fd0e5d746194c0197b61a07fb3d2bc86c92995f74132b7da45ae22bf64b18` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-05.zip` | 1571 | `44df260b8ad3cafbd6caa68abebf3ed396b6d2b8b318b1407f2a91f1de59e433` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-06.zip` | 1553 | `79a893dca04b146d6c36b0a67970f8592a05837c80bdabe93ece1c733b3220c3` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-07.zip` | 1484 | `e74e7262fb3981e1d771985e8a81c9d0ff49d472f58dd190edb23be506dc9a2f` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-08.zip` | 1498 | `59b3d0a61cfdde2e5f039bd2680b10b6772729591afd4cd4986c748b52f3dde2` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-09.zip` | 1558 | `ee6cbc03da315605318fe0fee0006aa41d33999b994c05247e3cdc1a358985b2` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-10.zip` | 1564 | `03d299c54cf9b27c1f3b4b384c52b5eec14549a94a9e126a3d9bdfa7443b5031` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-11.zip` | 1557 | `8cd1689c3542b2ab01c046b36a4f5ca3182ffd1ce68f4921d22162260657cff2` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-12.zip` | 1551 | `521f6ecb72d145fa84312506b9ddf5e3efd748a47a9e6dca406bcba601975b41` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-13.zip` | 1585 | `ad26ac505cf03efeeda4d19720eab0ed026a27687cea2ee2195fd8aa5c36c471` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-14.zip` | 1586 | `11e38aca2460476dcc1e88c090fc48e721b6ee6ca061eccf9e7f527c2a9b20e5` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-15.zip` | 1573 | `22213a9fe1030aa4bdae8173d5c120bbb4981dc0b39741be8f29dc0c3b46cf22` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-16.zip` | 1574 | `55c4814d119c2f7c20bcc76d0b3f6a730e91609db71a5f78137e41d05facb044` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-17.zip` | 1572 | `70161e89b4227bf476d3b75ba19123e9d49ada11d9946576f89d4e3f950919ad` | 24 |
| `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2026-11-18.zip` | 1564 | `95f07e863b2fe1961047fd303cc7f24dc48d2c0b21162e3ee907d94530f31dbb` | 24 |

### Monthly M15 (82 ZIP)

| S3 object key | Bytes | SHA-256 | Rows |
|---|---:|---|---:|
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-01.zip` | 139485 | `604e91a9db89202e87f10b610cf11d805a2a7915e28a07c53fc7d3921e384480` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-02.zip` | 131623 | `a89e0dfaf3bf187d4c86c0e96c2052110682f5980c370ece041184b4615b86d6` | 2784 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-03.zip` | 143581 | `da4596277f7e914e04497d36a733722b42a6c84b5710734e4076d50c0a6675b0` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-04.zip` | 138390 | `ebfe6813862b72c33b9defbc32317b89c0b59e03ec7d8b1a6cf4ff161716c100` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-05.zip` | 144024 | `8ef7d076102b7d7d5f0bbd6b0ac6b36d24c6194a4c51aa239ac68e614c1824b6` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-06.zip` | 135897 | `5674187f592088659d55aaabc8d684ba8b504e5bc7f9863b2a79ad91d46d21c3` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-07.zip` | 138871 | `82c2528648b7202e329e4eb42f59fa2972ee4f59ea4720139160a4e683535193` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-08.zip` | 142759 | `c3b8d9ff137e32f20b2793c4f7f7eed8bfd45648674f051cb51ce9e4ab366044` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-09.zip` | 138064 | `b23fd2d1b8d09f8d2b10308539bbc1023b29452f2ff5365fce5bb08b7888072a` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-10.zip` | 142405 | `723f3a5297b718ac1ea766933c12042f422ceb43f3dbfb1430e0ea5f55fa1e39` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-11.zip` | 142846 | `9442ac3d7c5aba02bfacfe0a35ce05756263e4f462a5a694941f27dfcd76f15d` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2020-12.zip` | 147987 | `c824e54aec2b63ace61d29166fcf12ac15729021b13bd1b5355f3825ecb50523` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-01.zip` | 152367 | `3aa4530f2afd42d8cae441d2634e81a6d733a49fd33970c705afee325e4aee2c` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-02.zip` | 137417 | `f0c941a7ecf452a3448e4a8951948518dd47e51ad7158629d5efcf410431939f` | 2688 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-03.zip` | 152137 | `d1c4cfa8137848dc3373753f8d0437eddf8db43b0e835efbc4a6da3af6935286` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-04.zip` | 146457 | `124fab2a0fe7525a5e7b2a1dbb2b776ce12e6003770dd930a10bbd56db4cdc79` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-05.zip` | 154209 | `f7ef372e125f87339f45fffaa329ea386d9e8be74998577fd75f807a90abae16` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-06.zip` | 148508 | `9853eae293ad9c5b4a1395fe6d5e6257bfd2ff27433c4ef00b0169b54853b7a2` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-07.zip` | 151061 | `86ef554b5c3c392cff96180db24268d9273905f3e8c2ed4d5e63904b0d798096` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-08.zip` | 151593 | `f6e0c79d84839f34de1c41993624b76b1c738101cf39622d31c926300681fc5a` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-09.zip` | 146664 | `5c74e804831937235287f424a0c34eddf525b3a366249037a34288c69b2cc6ed` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-10.zip` | 151726 | `6fbc1ced80b2d5b722114394ce145bfe4fbc40ad233b2ec0316d3bd45b8abcaa` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-11.zip` | 146206 | `8c3170955683fc914da107d67d8ebde0cda6f3a6250e9b4b5f6ceb94f5593712` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2021-12.zip` | 151429 | `a216bab60744f399e55561df822644029178827b352d1878fd6116082f70273d` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-01.zip` | 151020 | `46e0bc4607df992e4de6a6e76e2bf60b3a19db2b11f7b07d4a4bac4e26c6c35d` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-02.zip` | 135101 | `7b615ec48c6bc9f4a723e08d9990136554406640055c2fd084e0c0b63d405d74` | 2688 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-03.zip` | 146333 | `2ddcc24fbcf2661020a218f2251b1cb3af03bf32633efed028c0d0921468cafe` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-04.zip` | 140454 | `911e220f50a2a1798d35b31fce321cc4e61932a0a370c9e6837c27ff4dd8f0a8` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-05.zip` | 146513 | `31a46b1ac257f1690e6b16c606b2fde22aebf2d605047943d885bf28fe813389` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-06.zip` | 141973 | `7115895dc1e8425ee5ecedb18258e293decfc7769213362d928c42a29d8b6127` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-07.zip` | 145550 | `6cd98667f9b7a127a413bd061103800f2707921a9a231e18f47d71816ef86ac8` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-08.zip` | 143927 | `517e241a31c2062c50ca9861eb832fa9b3505b0ae67350135d5a74d812228eab` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-09.zip` | 139666 | `776bd8021ee4b7dd8dd6530bd8b0d4f4a3287df2a72810f5dcb26e35714c8903` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-10.zip` | 141497 | `bff25dbfad92e9c551ab77b6411e29462dbde298636144041a775330a126cd1b` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-11.zip` | 137846 | `7f74daa2a5f1631e5b60d0dd035dfb60c0d8e5f0105820484fde8b8914d07986` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-12.zip` | 137311 | `acf8b92a5cea478f7c32ab863b977836f629d4ff3373d20bb2b15673b57b87ae` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-01.zip` | 140488 | `7d9c643f940a65eaae7f8618a5f997ada493076a5f91b02bdd77b559d2ab2514` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-02.zip` | 129016 | `3d2bf498800e0526d9e7503d8f20f7dbd4fd1908e90570053a7ec5803b31118e` | 2688 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-03.zip` | 144941 | `843bdaf3f134e74e6f0efecf46dbd92952c61b9d57c6ce8b556392d81526ec48` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-04.zip` | 138552 | `4a9416010259d5219c25ba8d29eac0928ecf6876fc4d6cc751228110e97f5138` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-05.zip` | 142660 | `f584af353ef1a3bef7f45aa17d8826c622d04a2a817fe0c6289e37b933959b54` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-06.zip` | 138330 | `8fb734f8a60a161b2f17b5458ed3659017a61d2a5dd24d2d810243ce1f621032` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-07.zip` | 140229 | `c8df4ff96d804f2f57e51049bf94c11bf8bfa2f9333c0af29ab8f2504471966d` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-08.zip` | 138936 | `8ba91ecc5bf5573c3840a2f22f4b0b6d307fc659a9e11df3c3a6e7bcf332150f` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-09.zip` | 134048 | `f1f628bb4b1976ba632150bf999fde302ddcfc8899ff369a5119bdd5dba1e0d5` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-10.zip` | 140804 | `bf3f1b7d22b67155373cbc0334ec44c34c8861bf2127ccd432698d95aa31ead6` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-11.zip` | 136797 | `e70b84bec57cc0a76f9066cf5277b8c2ea3f4f4f03771f478a350160fa81b564` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2023-12.zip` | 143554 | `f6b191e620d269d229dee0c5b9abfb6e9610bd0a8e6718d2a96e0e820a013bb0` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-01.zip` | 145000 | `76953983fcd4cc35ac181c4a1c69d28cbb4ef8b983021aac84a111ea4e82ef69` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-02.zip` | 135641 | `f6a9399826f593aa23746d920e595e9705addd1154d4ec53fcf7a2564755e67b` | 2784 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-03.zip` | 147580 | `0f7dbdf7859f36d41c1444065409b2c9c4d66f5b3008647436fbc1b7a0d9f080` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-04.zip` | 141412 | `e1e52aa89d7004e4b93af4cfa5d8f03826881604bf2a990fd2f6979ed754c7ff` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-05.zip` | 144408 | `180775c3969d5e1a4f80dab6d62639945db50ed26b7fb240e66cc384d572295b` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-06.zip` | 137470 | `ff353ea993bd5db2ac704c7ab30b0f706216208da92089875daed06177b7a805` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-07.zip` | 145340 | `13cdc84f34becfaaaa9736896a0a0c92fa64bb20e84492569a1c1bb401634095` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-08.zip` | 145551 | `7db2001bc9958a0f42748ab56319a067be0610eb3f69ae7360251f9c54b933e1` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-09.zip` | 139696 | `ccc54f637eb90c3dd2bb190b3bfa40340c3812917726d203b5a9c94b8d27c727` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-10.zip` | 143532 | `64c3283e3e1020fb99916e908ec129c7ed2829319889db87319f3b48c72f6217` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-11.zip` | 141946 | `e54cdf3523373e2011ca133f12ee18ed54cf0e5a1a59426a9746fd2c39313a54` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2024-12.zip` | 146336 | `717d3e617fdc6f5c486c16d2f2c0e3e0929fd9158f75827bc603c003ad709544` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-01.zip` | 145675 | `0867b0b8e22069621de45df42cc49a8df1b8217cf777529b1df6d43253927588` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-02.zip` | 130972 | `44280cf80923ec6ee42e28e4606723b2f36909eab5c334ee5aee132ff989f12b` | 2688 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-03.zip` | 145535 | `aea345f1561a16710812658f2d435f0e02de5fc25d7ba8ad821526d67b2ab229` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-04.zip` | 140475 | `6a5166823a9e80e25f520a8e7e26f34550c975e26bd1c5bb95a20d530b89bfa5` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-05.zip` | 145447 | `303a174c2d15248fe00342ac2b01bec41bb4e11c4a5d26d480e2a382808bc020` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-06.zip` | 139881 | `4c980922647b630dbf146cb80934776930f8b4a9b419967710ecb8ce398e036d` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-07.zip` | 143938 | `dd5bb32a02e5a3dc93717530abe572f41e1bc50b920daad6e226bb6024e52b51` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-08.zip` | 144410 | `b8965932ae4008e4f1f8ec1ed344f11fbd1f743b44679dacfab665f05414aced` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-09.zip` | 138388 | `fcfe6d1c17890b82788b13707bbdc99694361f701a49f15347c8f0e85e55fd1f` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-10.zip` | 146246 | `14f11249137327f5ecadfaceab1eea9ba87f819298af645998fc9bd2cde02b77` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-11.zip` | 140773 | `66c714d54807c313814d0aef6ee2ef21e07e311605b47c23ae32978c721a4b23` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-12.zip` | 143001 | `d497e319364b0c13a0cd59e0192568ea1542e8f430844046189a8cf534895805` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-01.zip` | 142704 | `065fc8cf21f51ad6bd043fa670ba2dbc8c6030efd5dff63d5d4a9d99e0b88d0b` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-02.zip` | 131955 | `983c066f0cf0171466e89d7596433f5ac717ea8c805fe5b650a83b3176cd92c1` | 2688 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-03.zip` | 145250 | `ea25e84ddffdcc8b7ba68fb47363daee6a9ef53941f152c9ebf6d4e165d32bf8` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-04.zip` | 138462 | `0bc151133aa47be76f535539e25c04970bd6d0afd54e532951638dc8330fcc58` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-05.zip` | 142000 | `1c0a865f62ddca9890f5d7bbe901b7261a3818785594d960f5fce36ee7ce81f5` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-06.zip` | 139837 | `54369ae74f8122e0d3c8152807f78ec3ced435a8b0ab59c5efcea2cbad878857` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-07.zip` | 142057 | `10df439d8404a31fc55ed91fe0169b79db3fa3e7a8c83bc2eb704004eadea1c2` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-08.zip` | 141194 | `0702d68a42de591fb39929d10327f1258ce1d59b9d81158c07e412029eb36306` | 2976 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-09.zip` | 138273 | `e879fa6903fd905201bd1f59e456773638cdf8c13848da79331cee89b0046964` | 2880 |
| `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-10.zip` | 142135 | `4c146566bbff66b73f4058120be7d2188d7cef4d2fd7c0deab8308233de80b85` | 2976 |

### Monthly H1 (82 ZIP)

| S3 object key | Bytes | SHA-256 | Rows |
|---|---:|---|---:|
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-01.zip` | 37271 | `512a1d725c8df97a1bbbee4f118e730e9628500a8f271c9e59d2a7fc5fbfcfcc` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-02.zip` | 35268 | `13d067e5c7b258764b8524e1d3c61b129c44838c2ce9850f4d86cae13c61f198` | 696 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-03.zip` | 38166 | `9fc0c560cce35fd083febee10c0c8c3ffcd56a9185f9b489f265a51bbf60ec6e` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-04.zip` | 36833 | `bfa6d2adc1aefd8a96b3cbd38932486741caa1ae40f1e646df3606205402176f` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-05.zip` | 38289 | `1eb7de25a14b8a6c70098b866a21ba2c35f1b55c9e1c1d4dadb431cd4d3e180d` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-06.zip` | 36260 | `5f5b7ccd40facb7ddecd6019192be8de148e0aeeec8c8adc30cab3c474406c5b` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-07.zip` | 37043 | `f116be7c0a36e71f771ae4987b95e1f6d098dc0dae3b71154c12e7c390cf1a4c` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-08.zip` | 37996 | `d4dff9c958c878c00f2f3f059043612ac051fdc4117c3e9e74261db28c4f13fc` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-09.zip` | 36859 | `b210c5ecfae463aaef862ea0e6d8ccbf63430f32d6a80bad0bdeb2eef83a7165` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-10.zip` | 38117 | `753bc2e366777b40294690c5bbee38da8ec99e3157739ba0f16850c94ac92dc7` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-11.zip` | 37893 | `23694fa6fc619c159992db5325d37730a392e8ee23e9e5c375a7bfef6022fb82` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2020-12.zip` | 39316 | `9eca4954142f813a1ab404161b76facb56389a26fcd0b05bf93a19bf29578cb3` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-01.zip` | 40346 | `00de1eb2f3e3bc7f21b7ab321f1681385726fe7ba55306a7337acfd8f81fedfa` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-02.zip` | 36379 | `c5739d16db0aa917f9b4f196cf1dc3c9741b2889253c029571dcd2d00e83ccbb` | 672 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-03.zip` | 40163 | `518891de0fa643092cac84143c9b35a7cbcebfc75ae0846ce36c8e3adab1929f` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-04.zip` | 38669 | `0fdf8d01fa2eae368a63dcf709e6e6c5b0fd79bbe83b2f086aefbe2a7890924f` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-05.zip` | 40697 | `c209747915a1451a7b51d80d92e68332622c1dd1b9517dc7723f78cfa4f28ab9` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-06.zip` | 39207 | `5134cef4361e0819b721776da6e99f715141d122e3cfbf4be729e3dfc153ac33` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-07.zip` | 40038 | `97241c02191fd4694daf9836269e6f8ed04ef5bf858414de5a3354678552b54d` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-08.zip` | 40160 | `4c8290ad0baa9fcf37d45b893e8cae1a1e3b9ef77987a9d9abd64e44ab7deb09` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-09.zip` | 38738 | `22c55191129632daf70611af13e8f2b0f34a5e79f4876f41744a9848c43b9864` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-10.zip` | 40087 | `d3b55f8ae3689efe9bccc1d9b7082bda39fa7fa194e4c1197a63d1473ca57b4e` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-11.zip` | 38610 | `a013f6adfd3012130c0b0bc58895373ae478cd38c646ac87957b855682c7f069` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2021-12.zip` | 40053 | `f1dff81c6e322f7d5cee3c0808efd4e35b33e371f04ba613054264d9621318f1` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-01.zip` | 39953 | `5281a9c866e7d54b0a5b5e6a7dad5575ad7b96df67f05f74d614c54190ffff5f` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-02.zip` | 35964 | `b3a199287b2a8fed2c261999205d56cfd72ef9675c4b498a399601978d666228` | 672 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-03.zip` | 39024 | `f61ebcacd9a38f20b0ad89c64bbeb56baf368641fbbd6e25e987db2b96ede5ff` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-04.zip` | 37478 | `db7f9dbcc60cf68051b755346a5be32d27b0d3565cf6c02341b050a234ef44df` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-05.zip` | 39107 | `b1512041ade711819be114fee30668fbdd2783b73fa55607991ae14d1d43653f` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-06.zip` | 37922 | `1006ae5b8b4704da69f8f14fb4711d075d689fcf44cd0a98317df97953f1332d` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-07.zip` | 38784 | `72060f8608459b04817f652cbb945be28afef0ae54ccf38113911c194630c184` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-08.zip` | 38388 | `a1ad9eafd3dfecccfbc60c07de33ec2f7c33eab96f8ec04f88360b73b55dad76` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-09.zip` | 37283 | `92753ae32ed042ab7f10b90e3b9a49ddafc695c8e60eb563713855c73e2e6e82` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-10.zip` | 37838 | `d85a5f4bdbe93df2babdecf3b37f866655fa23c3fb31eeca96c3e3f6a1e9b872` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-11.zip` | 36889 | `e9b3f3b1929e3f6f255269c2d2eb564d9d9bcacbfc16651888e95765df383888` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-12.zip` | 36820 | `d313c2cb509cba13eff6538829245aedc993f18eff4a7bd48fe0eb6c3a9fa158` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-01.zip` | 37766 | `b9ac60cc3ffc1e16db96ca2314120ff7531988108ebef1733ee54234f4fedf7f` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-02.zip` | 34682 | `1ace9802f4da961db025a7b76a6171ef2c516c5307e5dee24267182f059110e0` | 672 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-03.zip` | 38700 | `35f0068cc41887ea11960c4bb10e251a404fef5ad4cb4c88699cc2419b6bc38b` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-04.zip` | 37139 | `ed6f0a84d1b2ed8f73fbdd4df10703e2ab49864fc4d657b0d8a9464a49dd4a29` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-05.zip` | 38198 | `2f278ad3ea09cc42e577ad7185de74391a1eb09b9d9836d375e2c540aef1667f` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-06.zip` | 37120 | `19bd435cdf58b426642c24a0df3b5fa755433f52a8c39f05dc5cfdeffa453aa0` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-07.zip` | 37558 | `ae9ebc03dff2bdeb805a1401b5cf1256b2b84283f5f9d92b1f454f33b223f499` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-08.zip` | 37282 | `599daa607ff593666036fe742d8272de6e0e9d284cd7d41d6585cf53baa20ca2` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-09.zip` | 35974 | `7849f82af86aabcb9a79f64d0527480f22117656a68f98280fe8b840a6ee1339` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-10.zip` | 37679 | `bbf0ef273c80f696ed9eb129a257812162487486692f124b9631ec38a924f6ae` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-11.zip` | 36685 | `26f1a2870f57925303edcf75581f0a33ff5e145c2126e15afc5fc1b400522428` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-12.zip` | 38475 | `5377bec9e6dc04027717836cc1c2a3789da4e4122d57e8395265a0414b766b7c` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-01.zip` | 38890 | `bf673f3d10804a951e8bac56dd2473486f113025971d43ebe5258ec40f9bfeb3` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-02.zip` | 36374 | `655ff5ac0fc570956756944c7afef4895c9bd149342f1e437de97292cbd1fe22` | 696 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-03.zip` | 39301 | `8138642b757ddf5a42207130277be4569afb4c581a0a1817be9f5f35a4415498` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-04.zip` | 37804 | `4bf3ca3574e0075c1b79f5b22c4253e26f6260f3621943205e3a8016c4c12318` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-05.zip` | 38427 | `1d607e3b26e6886ba742477bc97687f0b86c4c26ac564325dc5f1667e0362d35` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-06.zip` | 36794 | `7dba8642e56641fca2c7f3f363050ae88bf0d6c87d28e14b747fbd3267d4d3a8` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-07.zip` | 38700 | `920aacb84b2745ee8f31806a753cdc5b2d672e6814d9c50c0bf524ad45eb5611` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-08.zip` | 38718 | `8d8465eb4c8a4fd05ebc0126e4c14a217edb2039441546bf095229e975268de6` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-09.zip` | 37266 | `0a8118b3601f18ddad04a8afcf887fdc01661f66824a0ce49e0419be1f97f907` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-10.zip` | 38285 | `e3dcb9fe9d70fea19dfbdc5294044da69b9061c6f7411e99468825fac1ce8d61` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-11.zip` | 37741 | `0675e55056748489b8750cf6088a666f65dd4fd932d7ca5bd30491f5996b5f3d` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-12.zip` | 38950 | `b072f3147b3e390c81dcbf35830a12ff7d53a73236aa44a9eea78199502529cb` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-01.zip` | 38915 | `9ebc05c9b3d5ab3591edf65bc5c7e5dbc2f96c1efc4adc4ea198c651a99a41b1` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-02.zip` | 34861 | `077d761098eb5f2dbde65457833b9edab41ea6475284a77fcce0d4bec1bfb5cf` | 672 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-03.zip` | 38723 | `08043384c3336b0fa3eeee06e113a6f1eceb6d3fbe7b2971e9b9fa83625fdfb9` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-04.zip` | 37389 | `2adf7c1be412e43b04a128e997f4cb1e5e7f895f55b6e1bf66621807f221f274` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-05.zip` | 38805 | `2e736b9e792d5ae9d4607d7426e4530020762cb898d580b18d3fb0faf9d2ba8e` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-06.zip` | 37374 | `d1d9d5dbc540c19dd882305937f864f59ffffe3f5449a6b05b3f95efe7ca4fbc` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-07.zip` | 38443 | `3f471677b97cd3c5c21e9c1420bd7d58c1fe4041a3d2e195369277298ca01ea2` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-08.zip` | 38617 | `a240d3f766cd5c3db4e0702cf660ae54e327ec67aba169dda55abc90cae055f2` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-09.zip` | 37022 | `b15817c45e6ca13a907772591664a57e00b711fecbd4285f2a16ced3c7023019` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-10.zip` | 38885 | `b173469216acad36058ecfb0a5432471ec58b3c49032246d4d687dd3af8ae34a` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-11.zip` | 37564 | `75c4069b8ff93aa5e4064e885077426fd60f1cf6239a728b2d4ca543c0210d5a` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-12.zip` | 38148 | `41e977a06b7806ce1398aca5f9075befffd1e6303db891795f3b179c762709ec` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-01.zip` | 38152 | `6c15ac5fd895f26bf8e12b99df6ab9aff637dc94b37128e92c75c19887d0e3b3` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-02.zip` | 35154 | `886fca9764139a1d71d97ca28e0a2cb30fe7d6f44df9be2539452c02e3c4e775` | 672 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-03.zip` | 38671 | `41199df2dd62c333ea306d28de331bfffbbfed03609d100c63b2de1d173f7414` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-04.zip` | 36965 | `c822801b16eb317f4672e376a73664f2e5f9180409c57b6c7517707f4f873e8c` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-05.zip` | 37968 | `9a367708c90de999a7a9d3114fd111ff28203b13c8daef77d154b5216fb571f7` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-06.zip` | 37239 | `30bba473837a672a6a00a181a447446852414e6927bbda6684f873571788e9aa` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-07.zip` | 37864 | `a09f135066ace6925ce051ddbbdd4345c103423fbe35d32b568942de978dcc7c` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-08.zip` | 37864 | `b594301740cbb39818ba60f2835e4636aa06ad53308e25b1b312f1443fe0ccfe` | 744 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-09.zip` | 36887 | `07ab960882feb6d3120673a851f2a654c4c3f31f3a74d1f3fc4b0351a8ee1483` | 720 |
| `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-10.zip` | 37961 | `da0ec480b8857600067635308423022972e994d9dffe8b0251f0b7813018e2c8` | 744 |

## Governance status

- Payload retrieval and validation: **PASS**.
- Candle-level continuity within the retrieved period: **PASS**.
- Full-history completeness beyond the retrieved first/last candles: **NOT VERIFIED**.
- REST tail, SQLite dataset build, manifest publication to T0 data asset, Dropbox snapshot and restore: **NOT AUTHORIZED / NOT RUN**.
- Tests/workflows: no GitHub Actions workflow was run; this was a bounded data-validation task in isolated staging.
- Next permitted decision: review this evidence and separately approve any daily fallback for a specific monthly object, REST-tail retrieval, or SQLite build. No such work is implied by this PASS.
