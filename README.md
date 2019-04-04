# Testbench Generator for SystemVerilog modules

This python script takes in the SystemVerilog code for a module and creates a testbench from the module portlist. The testbench contains a clock and all the 

It can:
- Ignore comments (both // and /**/)
- Deal with arrays (e.g. wire [63:0] data)

It cannot (yet):
- Deal with types other than reg and wire
- Deal with parameters in the module declaration

Example:

The file

-------------------------
    /*
    This is counter with width WIDTH
    */
    module counter (
        input wire clk, res_n,
        output reg [WIDTH-1:0] cnt_out
        );                                   
        
        [...]
        
    endmodule
-------------------------

will produce this testbench:

-------------------------
    module counter_tb;
    
    reg clk; 
    reg res_n; 
    wire [WIDTH-1:0] cnt_out; 
    parameter PERIOD = 20;
    clock #(.PERIOD(PERIOD)) clk_I (clk);

    counter counter_I (
    .clk(clk),
    .res_n(res_n),
    .cnt_out(cnt_out));
    
    task initialise; 
        begin
            res_n <= 1;
            #PERIOD
            reset;
        end
    endtask
    
    task reset;
        begin
            @(negedge clk) res_n <= 0;
            #PERIOD
            @(negedge clk) res_n <= 1;
        end
    endtask

    endmodule
-------------------------

Notice how the testbench contains the following things:

1. Instance of the module under test
2. The task "reset" which pulls the reset for one period
3. The task "initialise" which initialises all regs in the testbench with 0, exept for active low signals whose names end in "_n" which are initialised with 1

It also creates a clock instance which might not be useful for others, especially if it is not called clock or your standard name for the clock signal is not clk. I'll try to make this more useful for other users at some point. But right now it's more for myself but feel free to copy and edit


