program SortRandom;
const
   MAX_SIZE = 100000;

type 
   ArrayType = array [1..MAX_SIZE] of longint;

var
   arr	: ArrayType;

procedure GenerateArray(var a : ArrayType);
var
   i	: longint;
   r	: real;
   seed	: longint;

   function random_number(limit	: longint): real;
   const
      IM = 139968;
      IA = 3877;
      IC = 29573;
   begin 
      seed := (seed * IA + IC) mod IM;
      random_number := limit * seed * (1 / IM)
   end; { random_number }

begin
   seed := 42;
   for i := 1 to MAX_SIZE do
   begin
      r := random_number(maxint);
      a[i] := round(r);
   end;
end;


Procedure BubbleSort(var a: ArrayType);
var
   i, j	: longint;
   temp	: longint;
begin
   for i := MAX_SIZE downto 1 do
      for j := 1 to i-1 do
	 if a[j] > a[j+1] then
	 begin
	    temp := a[j];
	    a[j] := a[j+1];
	    a[j+1] := temp;
          end;
  end; { BubbleSort }


begin
   WriteLn('N = ', MAX_SIZE);
   GenerateArray(arr);
   BubbleSort(arr);

   (*
   Write('Sorted integers: ');
   FOR i := 1 TO MAX_SIZE DO
      Write(arr[i], '  ');
   WriteLn;
   *)
end.

