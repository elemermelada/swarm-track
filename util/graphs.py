from tudatpy.kernel.interface import spice

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np


def plot_ephemeris(
    ax: Axes, ephemeris, axis=[1, 2], threeD=False, color="b", linestyle="-"
):
    if threeD:
        ax.plot(
            ephemeris[:, 0],
            ephemeris[:, 1],
            ephemeris[:, 2],
            color=color,
            linestyle=linestyle,
        )
        return ax
    ax.plot(
        ephemeris[:, axis[0]], ephemeris[:, axis[1]], color=color, linestyle=linestyle
    )
    return ax


def scatter_ephemeris(
    ax: Axes, ephemeris, axis=[1, 2], threeD=False, color="b", linestyle="-"
):
    if threeD:
        ax.scatter(
            ephemeris[:, 0],
            ephemeris[:, 1],
            ephemeris[:, 2],
            color=color,
            linestyle=linestyle,
        )
        return ax
    ax.scatter(
        ephemeris[:, axis[0]], ephemeris[:, axis[1]], color=color, linestyle=linestyle
    )
    return ax


def plot_trajectory_from_spice(
    ax: Axes,
    body,
    simulation_start_epoch,
    simulation_end_epoch,
    axis=[1, 2],
    threeD=False,
    color="b",
    linestyle="-",
):
    time2plt = np.arange(simulation_start_epoch, simulation_end_epoch, 60)
    ephemeris = list()
    for epoch in time2plt:
        ephemeris.append(
            spice.get_body_cartesian_position_at_epoch(
                target_body_name=body,
                observer_body_name="Mars",
                reference_frame_name="ECLIPJ2000",
                aberration_corrections="none",
                ephemeris_time=epoch,
            )
        )
    ephemeris = np.array(ephemeris) * 1e-3
    return plot_ephemeris(ax, ephemeris, axis, threeD, color, linestyle)


def plot_mars(ax: Axes, threeD=False):
    radius_mars = spice.get_average_radius("Mars")
    if threeD:
        ax.scatter(0, 0, 0, color="firebrick")
        return ax
    ax.add_patch(
        plt.Circle((0, 0), radius_mars * 1e-3, color="firebrick", label="Mars")
    )
    return ax


def init_trajectory_graph(threeD):
    if threeD:
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        return (ax, fig)

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))
    ax.axis("equal")
    ax.set_xlabel(r"$\Delta y$ [km]")
    ax.set_ylabel(r"$\Delta z$ [km]")
    ax.set_xlim(-1.0e4, 5.5e4)
    ax.set_ylim(-2.0e4, 2.0e4)
    ax.ticklabel_format(style="sci", scilimits=(0, 0), axis="both")

    return (ax, fig)
