/*
 * ML-DSA signature key generation, for libreswan
 *
 * Copyright (C) 2026 Sahana Prasad <sahana@redhat.com>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.  See <https://www.gnu.org/licenses/gpl2.txt>.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <prerror.h>
#include <prinit.h>
#include <keyhi.h>
#include <keythi.h>
#include <seccomon.h>
#include <secerr.h>
#include <secport.h>
#include <pk11pub.h>

#include "optarg.h"
#include "ttodata.h"
#include "constants.h"
#include "lswversion.h"
#include "lswalloc.h"
#include "lswlog.h"
#include "lswtool.h"
#include "lswnss.h"
#include "ipsecconf/keywords.h"		/* for KSF_NSSDIR */
#include "ipsecconf/setup.h"

#ifndef MAXBITS
# define MAXBITS 521
#endif

struct paramset {
	const char *name;
	CK_ML_DSA_PARAMETER_SET_TYPE type;
};

static const struct paramset paramsets[] = {
	{ "ml-dsa-44", CKP_ML_DSA_44, },
	{ "ml-dsa-65", CKP_ML_DSA_65, },
	{ "ml-dsa-87", CKP_ML_DSA_87, },
};

enum opt {
	OPT_DEBUG = 256,
	OPT_VERSION,
	OPT_VERBOSE,
	OPT_NSSDIR,
	OPT_NSSPW,
	OPT_SEEDDEV,
	OPT_SEEDBITS,
	OPT_HELP,
};

const struct option optarg_options[] = {
	{ OPT("debug", "help|<debug-flags>"), optional_argument, NULL, OPT_DEBUG, },
	{ "verbose\0",            no_argument,        NULL,   OPT_VERBOSE, },
	{ "help\0",               no_argument,        NULL,   OPT_HELP, },
	{ "version\0",            no_argument,        NULL,   OPT_VERSION, },
	NSS_OPTS,
	{ 0,            0,      NULL,   0, }
};
int nrounds = 30;               /* rounds of prime checking; 25 is good */

/* forwards */
static void mldsasigkey(CK_ML_DSA_PARAMETER_SET_TYPE paramset, struct logger *logger);
static const char *conv(const unsigned char *bits, size_t nbytes, int format);

int main(int argc, char *argv[])
{
	log_to_stderr = false;
	struct logger *logger = tool_logger(argc, argv);

	update_setup_option(KBF_SEEDBITS, DEFAULT_SEED_BITS);
	struct nss_flags nss = {0};

	while (true) {

		int c = optarg_getopt(logger, argc, argv);
		if (c < 0) {
			break;
		}

		switch ((enum opt)c) {
		case OPT_VERBOSE:       /* verbose description */
			log_to_stderr = true;
			continue;

		case OPT_DEBUG:
			optarg_debug(logger, OPTARG_DEBUG_YES);
			continue;

		case OPT_HELP:       /* help */
			optarg_usage("ipsec mldsasigkey", "[<paramset-name>]", "");

		case OPT_VERSION:       /* version */
			optarg_version("");

		case OPT_NSSDIR:       /* -d is used for nssdirdir with nss tools */
			optarg_nssdir(logger);
			continue;
		case OPT_NSSPW:       /* token authentication password */
			optarg_nsspw(logger, &nss);
			continue;

		case OPT_SEEDBITS: /* seed bits */
			optarg_seedbits(logger);
			continue;
		case OPT_SEEDDEV:       /* nonstandard random device for seed */
			optarg_seeddev(logger);
			continue;

		}

		bad_case(c);
	}

	CK_ML_DSA_PARAMETER_SET_TYPE paramset;
	if (argv[optind] == NULL) {
		paramset = paramsets[1].type; /* ml-dsa-65 */
	} else {
		paramset = 0;
		for (size_t i = 0; i < elemsof(paramsets); i++) {
			if (streq(argv[optind], paramsets[i].name)) {
				paramset = paramsets[i].type;
				break;
			}
		}
		if (paramset == 0) {
			fprintf(stderr,
				"%s: parameter set specification is malformed: %s\n",
				progname, argv[optind]);
			exit(1);
		}
	}

	/*
	 * Don't fetch the config options until after they have been
	 * processed, and really are "constant".
	 */

	init_nss(config_setup_nssdir(), nss, logger);

	mldsasigkey(paramset, logger);
	exit(0);
}

/*
 * generate an ML-DSA signature key
 */
static void mldsasigkey(CK_ML_DSA_PARAMETER_SET_TYPE paramset, struct logger *logger)
{
	SECKEYPrivateKey *privkey = NULL;
	SECKEYPublicKey *pubkey = NULL;

	PK11SlotInfo *slot = lsw_nss_get_authenticated_slot(logger);
	if (slot == NULL) {
		/* already logged */
		shutdown_nss();
		exit(1);
	}

	privkey = PK11_GenerateKeyPair(slot,
				       CKM_ML_DSA_KEY_PAIR_GEN,
				       &paramset, &pubkey,
				       PR_TRUE,
				       PK11_IsFIPS() ? PR_TRUE : PR_FALSE,
				       lsw_nss_get_password_context(logger));

	/* inTheToken, isSensitive, passwordCallbackFunction */
	if (privkey == NULL) {
		fprintf(stderr,
			"%s: key pair generation failed: \"%d\"\n", progname,
			PORT_GetError());
		shutdown_nss();
		exit(1);
	}

	PK11_FreeSlot(slot);

	char *hex_ckaid;
	{
		SECItem *ckaid = PK11_GetLowLevelKeyIDForPrivateKey(privkey);
		if (ckaid == NULL) {
			fprintf(stderr, "%s: 'CKAID' calculation failed\n", progname);
			exit(1);
		}
		hex_ckaid = strdup(conv(ckaid->data, ckaid->len, 16));
		SECITEM_FreeItem(ckaid, PR_TRUE);
	}

	PORT_Assert(pubkey != NULL);
	fprintf(stderr, "Generated ML-DSA key pair with CKAID %s was stored in the NSS database\n",
		hex_ckaid);
	fprintf(stderr, "The public key can be displayed using: ipsec showhostkey --left --ckaid %s\n",
		hex_ckaid);

	if (hex_ckaid != NULL)
		free(hex_ckaid);
	if (privkey != NULL)
		SECKEY_DestroyPrivateKey(privkey);
	if (pubkey != NULL)
		SECKEY_DestroyPublicKey(pubkey);

	shutdown_nss();
}

/*
   - conv - convert bits to output in specified datatot format
 * NOTE: result points into a STATIC buffer
 */
static const char *conv(const unsigned char *bits, size_t nbytes, int format)
{
	static char convbuf[MAXBITS / 4 + 50];  /* enough for hex */
	size_t n;

	n = datatot(bits, nbytes, format, convbuf, sizeof(convbuf));
	if (n > 0) {
		convbuf[n] = '\0';
	} else {
		convbuf[0] = '\0';
	}
	return convbuf;
}
