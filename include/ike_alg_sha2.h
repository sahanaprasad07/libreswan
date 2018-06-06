/*
 * Copyright (C) 2016 Andrew Cagney <cagney@gnu.org>
 * Copyright (C) 2016 Sahana Prasad <sahana.prasad07@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.  See <http://www.fsf.org/copyleft/gpl.txt>.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 *
 */
#include <pkcs11t.h>

extern const struct hash_desc ike_alg_hash_sha2_256;
extern const struct hash_desc ike_alg_hash_sha2_384;
extern const struct hash_desc ike_alg_hash_sha2_512;

extern const struct prf_desc ike_alg_prf_sha2_256;
extern const struct prf_desc ike_alg_prf_sha2_384;
extern const struct prf_desc ike_alg_prf_sha2_512;

extern const struct integ_desc ike_alg_integ_sha2_256;
extern const struct integ_desc ike_alg_integ_sha2_384;
extern const struct integ_desc ike_alg_integ_sha2_512;

extern const struct integ_desc ike_alg_integ_hmac_sha2_256_truncbug;

extern const CK_RSA_PKCS_PSS_PARAMS rsa_pss_sha2_256;
extern const CK_RSA_PKCS_PSS_PARAMS rsa_pss_sha2_384;
extern const CK_RSA_PKCS_PSS_PARAMS rsa_pss_sha2_512;
