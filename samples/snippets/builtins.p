Program BuiltinTest;

TYPE
   primarycolor = (red, yellow, blue);

   
Procedure AssertTrue(b : Boolean);
Begin
   If b Then
      Writeln('OK')
   Else
      Halt(1);
End; { AssertTrue }

Begin
   { 8.1.1 ORD }
   AssertTrue(Ord(5) = 5);
   AssertTrue(Ord('A') = 65);
   AssertTrue(Ord(red) = 0);
   AssertTrue(Ord(blue) = 2);

   
   { 8.1.4 CHR }
   AssertTrue(Chr(25H) = '%');
   AssertTrue(Chr(38H) = '8');
   AssertTrue(Chr(99) = 'c');
   
   { 8.1.5 PRED }
   AssertTrue(Pred(blue) = yellow);
   AssertTrue(Pred(yellow) = red);
   AssertTrue(Pred(red) = -1); { should cause an error }
   AssertTrue(Pred(True) = False);

   { 8.1.6 SUCC }
   AssertTrue(Succ(red) = yellow);
   AssertTrue(Succ(yellow) = blue);
   AssertTrue(Succ(blue) = 3); { should cause an error }
   AssertTrue(Succ(False) = True);
   
   { 8.2.1 ODD }
   AssertTrue(Odd(0));
   AssertTrue(Odd(7));
   AssertTrue(Odd(300));
   
   { 8.3.1 ABS }
   AssertTrue(Abs(-5) = 5);
   AssertTrue(Abs(3.777) = 3.777);
   AssertTrue(Abs(0) = 0);
   AssertTrue(Abs(-78000) = 78000);


   { 8.3.2 SQR }
   AssertTrue(Sqr(-5) = 25);
   AssertTrue(Sqr(1.2) = 1.44);
   AssertTrue(Sqr(0.0) = 0.0);
   AssertTrue(Sqr(-41000) = 1681000000);


   { 8.3.3 SQRT }
   AssertTrue(Sqrt(25) = 5.0);
   AssertTrue(Sqrt(1.44) = 1.2);
   AssertTrue(Sqrt(0.0) = 0.0);
   AssertTrue(Sqrt(1681000000) = 41000.0);


   { 8.3.4 EXP }
   AssertTrue(Exp(0) = 1.0);
   AssertTrue(Exp(1) >= 2.7182);
   AssertTrue(Exp(-1.0) >= 0.367878);
   AssertTrue(Exp(1) <= 2.7184);
   AssertTrue(Exp(-1.0) <= 0.367880);

   { 8.3.5 LN }
   AssertTrue(Ln(1) = 0.0);
   AssertTrue(Ln(2.7183) <= 1.00001);
   AssertTrue(Ln(2.7183) >= 0.99999);
   AssertTrue(Ln(0.367879) <= -0.99999);
   AssertTrue(Ln(0.367879) >= -1.00001); 

   { 8.3.6 SIN }
   AssertTrue(Sin(0.0) = 0.0);
   AssertTrue(Sin(3.1416) <= 0.00001);
   AssertTrue(Sin(3.1416) >= -0.00001);
   AssertTrue(Sin(-1) >= -0.84148);
   AssertTrue(Sin(-1) <= -0.84147);


   { 8.3.7 COS }
   AssertTrue(Cos(0.0) = 1.0);
   AssertTrue(Cos(3.1416) >= -1.0);
   AssertTrue(Cos(3.1416) <= -0.9999);
   AssertTrue(Cos(-1) <= 0.5404);
   AssertTrue(Cos(-1) >= 0.5403);

   { 8.3.8 TAN }
   AssertTrue(Tan(0.0) = 0.0);
   AssertTrue(Tan(3.1416) <= 0.00001);
   AssertTrue(Tan(3.1416) >= 0.0);

   { 8.3.9 ARCSIN }
   AssertTrue(ArcSin(0) = 0.0);
   AssertTrue(ArcSin(1) <= 1.5708);
   AssertTrue(ArcSin(1) >= 1.5707);

   { 8.3.10 ARCCOS }
   AssertTrue(ArcCos(1) = 0.0);
   AssertTrue(ArcCos(0) <= 1.5708);
   AssertTrue(ArcCos(0) >= 1.5707);

   { 8.3.11 ARCTAN }
   AssertTrue(ArcTan(0) = 0.0);
   AssertTrue(ArcTan(1) <= 0.7854);
   AssertTrue(ArcTan(1) >= 0.7853);

   { 8.4.1 TRUNC }
   AssertTrue(Trunc(3.7) = 3);
   AssertTrue(Trunc(-3.7) = -3);

   { 8.4.2 LTRUNC }
   AssertTrue(LTrunc(69553.0787) = 69553);
   AssertTrue(LTrunc(-824000.9215) = -824000);

   { 8.4.3 ROUND }
   AssertTrue(Round(3.2) = 3);
   AssertTrue(Round(-3.7) = -4);

   { 8.4.4 LROUND }
   AssertTrue(LRound(69553.0787) = 69553);
   AssertTrue(LRound(-824000.9215) = -824001);

   AssertTrue(Size(1) = 2);
End.