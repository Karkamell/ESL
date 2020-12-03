from pygmyhdl import *

@chunk
def dff(clk_i, d_i, q_o):

    @seq_logic(clk_i.posedge)
    def logic():
        q_o.next = d_i


@chunk
def register(clk_i, d_i, q_o):
    for k in range(len(d_i)):
        dff(clk_i, d_i.o[k], q_o.i[k])


initialize()  # Initialize for simulation.

# Create clock signal and 8-bit register input and output buses.
clk = Wire(name='clk')
data_in = Bus(8, name='data_in')
data_out = Bus(8, name='data_out')

register(clk_i=clk, d_i=data_in, q_o=data_out)

from random import randint  # Random integer function.


def test_bench():
    # Apply ten random inputs to the register.
    for i in range(10):
        data_in.next = randint(0, 256)  # Set register input to a random 8-bit value.
        clk.next = 0  # Lower clock signal to 0.
        yield delay(1)  # Wait for one unit of simulation time.
        clk.next = 1  # Then raise the clock signal to 1 ...
        yield delay(1)  # ... and wait one more time unit. The register output should change.



simulate(test_bench())


@chunk
def full_adder_bit(a_i, b_i, c_i, s_o, c_o):

    @comb_logic
    def logic():
        # Exclusive-OR (^) the inputs to create the sum bit.
        s_o.next = a_i ^ b_i ^ c_i
        # Generate a carry output if two or more of the inputs are 1.
        # This uses the logic AND (&) and OR (|) operators.
        c_o.next = (a_i & b_i) | (a_i & c_i) | (b_i & c_i)


initialize()  # Initialize for a new simulation.

# Declare input and output signals for the full-adder bit.
a_i, b_i, c_i = Wire(name='a_i'), Wire(name='b_i'), Wire(name='c_i')
sum_o, c_o = Wire(name='sum_o'), Wire(name='c_o')

# Instantiate a full-adder bit with the I/O connections.
full_adder_bit(a_i, b_i, c_i, sum_o, c_o)

# Simulate the full-adder bit operation for every possible combination
# of the a_i, b_i and c_i inputs.
exhaustive_sim(a_i, b_i, c_i)

# Show the response of the full-adder bit to the inputs.
show_text_table()


@chunk
def adder(a_i, b_i, s_o):

    # Create a bus for the carry bits that pass from one stage to the next.
    # There is one more carry bit than the number of adder stages in order
    # to drive the carry input of the first stage.
    c = Bus(len(a_i) + 1)

    # Set the carry input to the first stage of the adder to 0.
    c.i[0] = 0

    # Use the length of the a_i input bus to set the loop counter.
    for k in range(len(a_i)):
        # The k-th bit of the a_i and b_i buses are added with the
        # k-th carry bit to create the k-th sum bit and the
        # carry output bit. The carry output is the
        # carry input to the (k+1)-th stage.
        full_adder_bit(a_i=a_i.o[k], b_i=b_i.o[k], c_i=c.o[k], s_o=s_o.i[k], c_o=c.i[k + 1])


initialize()  # Once again, initialize for a new simulation.

# Declare 8-bit buses for the two numbers to be added and the sum.
a = Bus(8, name='a')
b = Bus(8, name='b')
s = Bus(8, name='sum')

# Instantiate an adder and connect the I/O buses.
adder(a, b, s)

# Simulate the adder's output for 20 randomly-selected inputs.
random_sim(a, b, num_tests=20)

# Show a table of the adder output for each set of inputs.
show_text_table()


@chunk
def counter(clk_i, cnt_o):

    # The length of the counter output determines the number of counter bits.
    length = len(cnt_o)

    one = Bus(length, init_val=1)  # A constant bus that carries the value 1.
    next_cnt = Bus(length)  # A bus that carries the next counter value.

    # Add one to the current counter value to create the next value.
    adder(one, cnt_o, next_cnt)

    # Load the next counter value into the register on a rising clock edge.
    register(clk_i, next_cnt, cnt_o)


@chunk
def blinker(clk_i, led_o, length):

    cnt = Bus(length, name='cnt')  # Declare the counter bus with the given length.
    counter(clk_i, cnt)  # Instantiate a counter of the same length.

    # Attach the MSB of the counter bus to the LED output.
    @comb_logic
    def output_logic():
        led_o.next = cnt[length - 1]


initialize()                 # Initialize for simulation.
clk = Wire(name='clk')       # Declare the clock input.
led = Wire(name='led')       # Declare the LED output.
blinker(clk, led, 3)         # Instantiate a three-bit blinker and attach I/O signals.
clk_sim(clk, num_cycles=16)  # Apply 16 clock pulses.
show_waveforms()             # Look at the waveforms.

toVerilog(blinker, clk_i=clk, led_o=led, length=22)
