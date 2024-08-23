#ifndef POINTS_H
#define POINTS_H

#include <stdio.h>
#include <stdbool.h>

#include "models.h"

void xMUL_pos(proj *T, proj const *A24, int Aaffine, int pos_li);

void xMUL_pos_const(proj *T, proj const *A24, int Aaffine, int pos_li, int pos_batch);

bool is_at_infinity(proj *Q);

void clear_power_two(proj *T, proj const *A24, int Aaffine);

bool is_li_order(proj *Q, proj const *A24, int Aaffine, int pos_li);

#endif
