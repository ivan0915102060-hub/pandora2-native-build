# Public protected-AWG qualification candidate

This repository payload contains only the reviewed workflow, narrow public-source derivative patches, exact source identities and read-only verification scripts. It contains no PANDORA application, Authority state, device credentials, private keys or formal data.

Upstream Android commit: 5c16489e2cd9ed3a0a7a27c7445bba5238132f86 (Apache-2.0).
Upstream Go commit: 1b86b2ae0e493e7ea93f8c1a0f0cb6735b1551f1 (MIT).
Keep the upstream license notices in the derivative patch; build artifacts include both upstream licenses.

Manual only, one free ubuntu-24.04 job, 30 minutes, contents:read, no secrets, explicit SDK/free-budget/public-patch gates, artifact retention one day. No dispatch is authorized by the existence of this payload.

The proposed job runs only the new Linux conn/tun tests and compiles an unsigned Android library, then reads its bytecode/ELF symbols without executing Android JNI. Android callbacks, JNI lifecycle, Binder/FD, real protection, native qualification and phone operation remain NOT_RUN. Successful compilation does not authorize production nativeStart.
