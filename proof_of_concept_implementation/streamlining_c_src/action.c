#include <assert.h>
#include "action.h"
#include "points.h"
#include "elliptic_curve.h"
#include "externalfun.h"
#include "helper.h"

/* totally not constant-time. */
void xISOG_matryoshka_pos(proj *A, proj *P, long long Plen, proj *Qker, int pos_li){
    long long Qker_degree = primes[pos_li];
    // printf("xISOG_matryoshka_pos: Qker_degree = %ld\n", Qker_degree);
    xISOG_matryoshka(A, P, Plen, Qker, Qker_degree, Qker_degree, Qker_degree);
}

void xISOG_matryoshka_pos_const(proj *A, proj *P, long long Plen, proj *Qker, int pos_li, int pos_lwr, int pos_luper){
    long long Qker_degree = primes[pos_li];
    long long klower = primes[pos_lwr];
    long long kupper = primes[pos_luper];
    xISOG_matryoshka(A, P, Plen, Qker, Qker_degree, klower, kupper);
}

/* totally not constant-time. */
void action_old(public_key *out, public_key const *in, private_key const *priv)
{
    uintbig k[2];
    uintbig_set(&k[0], 4); /* maximal 2-power in p+1 */
    uintbig_set(&k[1], 4); /* maximal 2-power in p+1 */

    uint8_t e[2][primes_num];

    for (int64_t i = 0; i < primes_num; ++i) {

        int8_t t = priv->e[i];

        if (t > 0) {
            e[0][i] = t;
            e[1][i] = 0;
            uintbig_mul3_64(&k[1], &k[1], primes[i]);
        }
        else if (t < 0) {
            e[1][i] = -t;
            e[0][i] = 0;
            uintbig_mul3_64(&k[0], &k[0], primes[i]);
        }
        else {
            e[0][i] = 0;
            e[1][i] = 0;
            uintbig_mul3_64(&k[0], &k[0], primes[i]);
            uintbig_mul3_64(&k[1], &k[1], primes[i]);
        }
    }

    proj A = {in->A, fp_1};

    bool done[2] = {false, false};

    do {

        assert(!memcmp(&A.z, &fp_1, sizeof(fp)));
        
        // proj P;
        // fp_random(&P.x);
        // P.z = fp_1;      

        // fp rhs;
        // montgomery_rhs_v2(&rhs, &A.x, &P.x);
        // bool sign = !fp_sqrt(&rhs);
        // if (done[sign])
        //     continue;
        
        bool sign = rand() % 2;
        if (done[sign])
            continue;
        proj P;
        proj Ppm[2]; //added
        elligator(&Ppm[0],&Ppm[1],&A); //added
        P = Ppm[sign];

        xMUL_vartime(&P, &A, 0, &P, &k[sign]);

        done[sign] = true;

        for (int64_t i = primes_num-1; i >= 0; --i) {  //changed loop direction

            if (e[sign][i]) {

                uintbig cof = uintbig_1;
                for (int64_t j = i - 1; j >= 0; --j)   //changed loop direction
                    if (e[sign][j])
                        uintbig_mul3_64(&cof, &cof, primes[j]);

                proj K;
                xMUL_vartime(&K, &A, 0, &P, &cof);

                if (memcmp(&K.z, &fp_0, sizeof(fp))) {

                    xISOG(&A, &P, 1, &K, primes[i]);

                    if (!--e[sign][i])
                        uintbig_mul3_64(&k[sign], &k[sign], primes[i]);

                }

            }

            done[sign] &= !e[sign][i];
        }

        fp_inv(&A.z);
        fp_mul2(&A.x, &A.z);
        A.z = fp_1;

    } while (!(done[0] && done[1]));

    out->A = A.x;
}
