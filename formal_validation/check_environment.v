(* check_environment.v - Check what's available *)

(* Try the simplest import first *)
Require Import Coq.Init.Datatypes.
Require Import Coq.Init.Nat.

(* Check if basic types work *)
Compute 42.
Check nat.
Check bool.

(* Try to find string *)
Print Coq.Strings.String.