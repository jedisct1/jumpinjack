Jumpin' Jack
============

Jumpin' Jack is a trivial and ugly, but still maybe potentially useful script to uncover conditional jumps added by smart compilers.

This can be useful if the original intent was to build constant-time code.

It was designed to check C/C++ code, but it might work with other compiled languages as well.

Usage
-----

* Disassemble the compiled library to analyze using binutils'`objdump` (`gobjdump` from `binutils` on MacOS):

```sh
objdump -d -l /usr/local/lib/libfoo.so > foo.odump
```

* Create annotated shadow copies of the source code:

```sh
python jumpinjack.py -b /path/to/the/source/code -d foo.odump
```

Annotated copies have a `.tagged` suffix. Review these by grepping for `JJ: JUMP` trailing comments. All of these indicate conditional jumps inserted by the compiler:

```c
i = len;
while (i != 0U) {   /*** JJ: JUMP (jne 21368 <sodium_compare+0x25>) ***/
    i--;
    x1 = b1[i];
    x2 = b2[i];
    gt |= ((x2 - x1) >> 8) & eq;
    eq &= ((x2 ^ x1) - 1) >> 8;
}
return (int) (gt + gt + eq) - 1;
```

Conditional jumps right before or after an actual control flow statement are expected. However, you may also stumble upon lines annoted with `JJ: JUMP!` (note the exclamation mark):

```c
a  = f[0] * sn;
h0 = ((uint64_t) a) & mask; /*** JJ: JUMP! (jne 1d4c1 <crypto_scalarmult_curve25519_ref10+0x19f>) ***/
```

You should carefully review these first and they are more likely to contain conditional jumps inserted by the compiler, that are not explicitly visible in the source code.

Jumpin' Jack can also be useful to discover interesting loop optimizations performed by the compiler, such as:

```c
for (i = 63; i != 0; i--) {
    ge25519_select(&t, pi, e[i]);
    ge25519_madd(&r, h, &t);

    ge25519_p1p1_to_p2(&s, &r);	/*** JJ: JUMP! (jne 10a38 <ge25519_scalarmult+0x285>) ***/
    ge25519_p2_dbl(&r, &s);
    ge25519_p1p1_to_p2(&s, &r);
    ge25519_p2_dbl(&r, &s);
    ge25519_p1p1_to_p2(&s, &r);
    ge25519_p2_dbl(&r, &s);
    ge25519_p1p1_to_p2(&s, &r);
    ge25519_p2_dbl(&r, &s);
    ge25519_p1p1_to_p3(h, &r);
}
ge25519_select(&t, pi, e[i]);
ge25519_madd(&r, h, &t);

ge25519_p1p1_to_p3(h, &r);
```

The compiler noticed code right after the loop identical to the one at the beginning of the loop, and inserted the conditional jump right after it, removing the second occurrence.
