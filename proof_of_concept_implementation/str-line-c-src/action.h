#ifndef ACTION_H
#define ACTION_H

// #include <stdint.h>
#include "models.h"

void xISOG_matryoshka_pos(proj *A, proj *P, long long Plen, proj *Qker, int pos_li);
void xISOG_matryoshka_pos_const(proj *A, proj *P, long long Plen, proj *Qker, int pos_li, int pos_lwr, int pos_luper);

void action_old(public_key *out, public_key const *in, private_key const *priv);
#endif // HELPER_H