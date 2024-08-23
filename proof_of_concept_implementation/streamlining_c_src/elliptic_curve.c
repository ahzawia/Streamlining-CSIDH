#include "elliptic_curve.h"
#include "externalfun.h"

void to_public_key(public_key *pub, proj const *E){
  proj E_temp;
  
  E_temp = *E;
  fp_inv(&E_temp.z);
  fp_mul2(&E_temp.x,&E_temp.z);
  E_temp.z = fp_1;

  pub->A = E_temp.x;
}

bool EC_validate(proj const *E){
  public_key pub;
  to_public_key(&pub, E);
  return validate(&pub);
}