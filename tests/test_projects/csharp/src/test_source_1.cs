using System;

namespace SampleProject
{
    public class MathUtils
    {
        // Static function
        public static int Add(int a, int b)
        {
            return a + b;
        }

        // Regular instance function
        public int Multiply(int a, int b)
        {
            return a * b;
        }
    }

    public class Greeter
    {
        // Static function
        public static void SayHello()
        {
            Console.WriteLine("Hello, world!");
        }

        // Regular instance function
        public void Greet(string name)
        {
            Console.WriteLine($"Hello, {name}!");
        }
    }

    // Top-level static class
    public static class Utility
    {
        public static void PrintVersion()
        {
            Console.WriteLine("Version 1.0");
        }
    }
}