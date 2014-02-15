(*****************************************************************************
 * A simple bubble sort program.  Reads integers, one per line, and prints   *
 * them out in sorted order.  Blows up if there are more than 49.            *
 *****************************************************************************)
PROGRAM Sort(input, output);
CONST
   (* Max array size. *)
   MaxElts	= 50;
TYPE 
   (* Type of the element array. *)
   IntArrType = ARRAY [1..MaxElts] OF Integer;

VAR
   (* Indexes, exchange temp, array size. *)
   i, j, tmp, size	: integer;
   (* Array of ints *)
   arr: IntArrType;

(* Read in the integers. *)
PROCEDURE ReadArr(VAR size: Integer; VAR a: IntArrType);
var
   rc : integer;
BEGIN 
   size := 0;
   REPEAT
      rc := readln(a[size + 1]);
      IF rc = 1 THEN 
	 size := size + 1;
   UNTIL rc <= 0
END;
BEGIN
   (* Read *)
   ReadArr(size, arr);

   (* Sort using bubble sort. *)
   FOR i := size - 1 DOWNTO 1 DO
      FOR j := 1 TO i DO 
	 IF arr[j] > arr[j + 1] THEN BEGIN
	    tmp := arr[j];
	    arr[j] := arr[j + 1];
	    arr[j + 1] := tmp;
	 END;
   
   (* Print. *)
   FOR i := 1 TO size DO
      writeln(arr[i])
END.
