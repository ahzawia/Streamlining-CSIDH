#ifndef ELLIPTIC_CURVE_H
#define ELLIPTIC_CURVE_H

#include <stdbool.h>
#include "models.h"

void to_public_key(public_key *pub, proj const *E);
bool EC_validate(proj const *E);


#endif