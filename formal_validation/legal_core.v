(** 统一事实模型：扩张解释下的法律范畴论 **)

Require Import Coq.Lists.List.
Import ListNotations.

(** 1. 本体定义：将 (1)-(5) 与实体全部统一为原子类型 **)

Inductive AtomType : Type :=
  | Entity_Obj    (* 实体：实在客体或抽象权利 *)
  | Process_Obj   (* (1) 过程：作为客体存在的程序 *)
  | Event_Obj     (* (2) 事件：作为客体存在的发生 *)
  | State_Obj     (* (3) 状态：法律存续的样态 *)
  | Property_Obj  (* (4) 属性：客体的法律特征 *)
  | Relation_Obj. (* (5) 关系：主体间的法律纽带 *)

(** 2. 事实定义：递归构造 **)

Inductive Fact : Type :=
  | Atom    : AtomType -> Fact        (* 所有的客体直接就是事实 *)
  | Evolve  : Fact -> Fact -> Fact    (* 事实间的演变，即动态事实 *)
  | Aggregate : list Fact -> Fact.    (* 事实的集合/过程流 *)

(** 3. 范畴公理：定义事实空间中的态射 **)

Parameter Morphism : Fact -> Fact -> Type.

Section CategoryAxioms.
  Axiom Identity : forall (A : Fact), Morphism A A.
  
  Axiom Compose : forall {A B C : Fact}, 
    Morphism A B -> Morphism B C -> Morphism A C.

  Axiom Associativity : forall {A B C D : Fact} 
    (f : Morphism A B) (g : Morphism B C) (h : Morphism C D),
    Compose f (Compose g h) = Compose (Compose f g) h.
End CategoryAxioms.

(** 4. 属性关联逻辑：目视验证的核心 **)

Section Logic.
  (* has_property 现在连接的是 Fact 与其对应的 AtomType 描述 *)
  Parameter has_attr : Fact -> AtomType -> Prop.

  (* 扩张解释验证：属性 (4) 也是一个 Fact *)
  Definition Attribute_As_Fact (attr : AtomType) : Fact := Atom attr.

  (* 验证：从实体事实推导出其属性事实的态射 *)
  Theorem attribute_inference : forall (f : Fact) (a : AtomType),
    has_attr f a -> Morphism f (Atom a).
  Admitted.
End Logic.

(** 5. 实例化示例（用于目视验证） **)

Definition MyEntity   := Atom Entity_Obj.
Definition MyProperty := Atom Property_Obj.
Definition MyRelation := Atom Relation_Obj.

(* 一个复杂的法律事实：由实体和属性构成的事件 *)
Definition Ownership_Event := Evolve MyEntity MyProperty.

Check Ownership_Event.